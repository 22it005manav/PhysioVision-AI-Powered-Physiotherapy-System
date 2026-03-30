from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, Optional
from datetime import datetime, timezone
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/PhysioVision")

RAG = None
EmbeddingGenerator = None
try:
    # Works when app is started as a package module (e.g. uvicorn app.main:app)
    from .chatbot import RAG as _RAG, EmbeddingGenerator as _EmbeddingGenerator
    RAG = _RAG
    EmbeddingGenerator = _EmbeddingGenerator
except Exception as e:
    print(f"Warning: Chatbot dependencies unavailable. Chat endpoints disabled: {e}")
import json
import re
import time
import uvicorn


# Initialize FastAPI app
app = FastAPI()


# Initialize RAG components only if chatbot module loaded successfully.
if RAG is not None:
    try:
        Ragbot = RAG()
        Ragbot.load_documents()
        print("RAG bot initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize RAG bot: {e}")
        Ragbot = None
else:
    Ragbot = None

if EmbeddingGenerator is not None:
    try:
        embedding_generator = EmbeddingGenerator()
        print("Embedding generator initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize embedding generator: {e}")
        embedding_generator = None
else:
    embedding_generator = None

uri = MONGODB_URI

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
db = None
collection_users = None
physical_attributes_collection = None
WeeklyPlan_collection = None

# Simple in-memory cache for fast repeated chatbot queries.
CHAT_CACHE = {}
CACHE_TTL_SECONDS = 120
MAX_CACHE_ENTRIES = 200


def _normalize_chat_key(username: str, user_input: str) -> str:
    normalized = re.sub(r"\s+", " ", (user_input or "").strip().lower())
    return f"{username.strip().lower()}::{normalized}"


def _get_cached_chat_response(username: str, user_input: str):
    key = _normalize_chat_key(username, user_input)
    item = CHAT_CACHE.get(key)
    if not item:
        return None

    if time.time() - item["timestamp"] > CACHE_TTL_SECONDS:
        CHAT_CACHE.pop(key, None)
        return None

    return item["response"]


def _set_cached_chat_response(username: str, user_input: str, response: str):
    if len(CHAT_CACHE) >= MAX_CACHE_ENTRIES:
        oldest_key = min(CHAT_CACHE, key=lambda k: CHAT_CACHE[k]["timestamp"])
        CHAT_CACHE.pop(oldest_key, None)

    key = _normalize_chat_key(username, user_input)
    CHAT_CACHE[key] = {
        "response": response,
        "timestamp": time.time(),
    }


def _detect_chat_intent(user_input: str) -> str:
    text = (user_input or "").lower()

    if any(word in text for word in ["diet", "nutrition", "food", "meal", "protein"]):
        return "nutrition"
    if any(word in text for word in ["pain", "knee", "back", "shoulder", "injury"]):
        return "pain"
    if any(word in text for word in ["exercise", "plan", "workout", "session", "reps", "stretch"]):
        return "exercise"

    return "general"


def _needs_clarification(user_input: str) -> bool:
    words = [w for w in re.split(r"\s+", (user_input or "").strip()) if w]
    return len(words) < 4


def _format_structured_response(summary: str, intent: str) -> str:
    base_actions = {
        "nutrition": [
            "Add protein to each meal (eggs, yogurt, lentils, chicken, fish).",
            "Drink water regularly and include vegetables in at least 2 meals.",
            "Keep portions balanced: protein + fiber + complex carbs.",
        ],
        "pain": [
            "Use slow, controlled movement and avoid sharp-pain positions.",
            "Start with gentle mobility and low-impact strengthening.",
            "Reduce intensity if pain increases during or after exercise.",
        ],
        "exercise": [
            "Begin with 5-10 minutes warm-up before working sets.",
            "Do 2-3 focused exercises with controlled reps and rest.",
            "Track pain/fatigue score after session to adjust load safely.",
        ],
        "general": [
            "Share your goal (pain relief, strength, mobility, or weight management).",
            "Share your available daily time and any movement limitations.",
            "I can then provide a more precise plan and progression.",
        ],
    }

    actions = base_actions.get(intent, base_actions["general"])
    action_block = "\n".join([f"- {item}" for item in actions])

    return (
        f"Summary: {summary}\n\n"
        f"Action Steps:\n{action_block}\n\n"
        "Safety: Stop any movement that causes sharp pain and seek professional guidance if symptoms persist."
    )


def _build_clarifying_prompt(user_profile: Optional[dict] = None) -> str:
    name = (user_profile or {}).get("name")
    greeting = f" {name}" if name else ""
    return (
        f"Hi{greeting}! To give you a fast and accurate answer, please share:\n"
        "- Your goal (pain relief, strength, mobility, or nutrition)\n"
        "- Pain area/severity (if any)\n"
        "- Available daily time\n"
        "- Any movement restrictions"
    )


def ensure_db_ready():
    if collection_users is None:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Please start MongoDB and restart backend.",
        )


@app.on_event("startup")
def startup_db_client():
    global client, db, collection_users, physical_attributes_collection,WeeklyPlan_collection
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        db = client["PhysioVision"]
        collection_users =  db["Users"]   
        physical_attributes_collection = db["User_PhysicalAttributes"]
        WeeklyPlan_collection = db["User_WeeklyPlan"]
        print("Connected to MongoDB database.")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB at {uri}: {e}")
        print("Running in fallback mode - some features may be limited")
        db = None


# Pydantic Model for Validation
class HealthData(BaseModel):
    username: str
    sex: Literal["Female", "Male"]
    age: conint(ge=0)  # Ensures age is a non-negative integer
    height: confloat(ge=50, le=250)  # Ensures height is within range 
    hypertension: Literal["Yes", "No"]  # Changed to match frontend
    diabetes: Literal["Yes", "No"]  # Changed to match frontend
    bmi: confloat(ge=10, le=50) 
    pain_level: Literal["Chronic", "Acute"]  # Fixed spelling from "Acronic" to "Chronic"
    pain_category: Literal["Almost Perfect", "Immovable", "On your feet"]

@app.post("/update-field")
async def add_health_data(data: HealthData):
    # Check if the user exists in the "users" collection
    user = collection_users.find_one({"username": data.username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert the Pydantic data to a dictionary
    health_data = data.dict()

    # Update or insert the health data in the "physical_attributes" collection
    result = physical_attributes_collection.update_one(
        {"username": data.username},  # Find document by username
        {"$set": health_data},  # Update fields with new data
        upsert=True  # Insert if not exists
    )

    return {"message": "Health data updated successfully"}

# Pydantic model for sign-in request data
class UserSignIn(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    email: str
    new_password: str

@app.post("/api/signin")
async def sign_in(user: UserSignIn):
    ensure_db_ready()

    username = (user.username or "").strip()
    password = user.password or ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    # Find the user in the database
    existing_user = collection_users.find_one({"username": username})

    if not existing_user:
        raise HTTPException(status_code=400, detail="Username does not exist.")

    # Compare passwords directly (no hashing)
    if password != existing_user["password"]:
        raise HTTPException(status_code=400, detail="Incorrect password.")

    # Return success response
    return {
        "message": "Login successful",
        "success": True,
        "user": {
            "username": existing_user["username"]
        }
    }


@app.post("/api/reset-password")
async def reset_password(payload: PasswordResetRequest):
    ensure_db_ready()

    existing_user = collection_users.find_one({"email": payload.email})

    if not existing_user:
        raise HTTPException(status_code=404, detail="No account found for this email.")

    if not payload.new_password or len(payload.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 6 characters long.",
        )

    collection_users.update_one(
        {"email": payload.email},
        {"$set": {"password": payload.new_password}},
    )

    return {"message": "Password reset successful. Please sign in with your new password."}


# Pydantic model
class UserSignUp(BaseModel):
    name: str
    username: str
    email: str
    password: str


# User sign-up route
@app.post("/api/signup")
async def sign_up(user: UserSignUp):
    ensure_db_ready()

    name = (user.name or "").strip()
    username = (user.username or "").strip()
    email = (user.email or "").strip().lower()
    password = user.password or ""

    if not name or not username or not email or not password:
        raise HTTPException(status_code=400, detail="Name, username, email and password are required.")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    if "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address.")

    # Check if username or email already exists
    existing_user = collection_users.find_one({"username": username})
    existing_email = collection_users.find_one({"email": email})

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists. Try another one.")

    if existing_email:
        raise HTTPException(status_code=400, detail="A user is already registered with this email. Try another one.")

    # Convert Pydantic model to dictionary
    user_data = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
    }
    collection_users.insert_one(user_data)
    return {
        "message": "User registered successfully!",
        "success": True,
        "user": {"username": username},
    }
    
    

@app.get("/api/user/{username}")
async def get_user_details(username: str):
    # Fetch user details from 'Users' collection
    user = collection_users.find_one(
        {"username": username}, 
        {"_id": 0, "password": 0}  # Exclude sensitive fields
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Fetch user physical attributes from 'User_PhysicalAttributes' collection
    collection_physical_attributes = db["User_PhysicalAttributes"]
    physical_attributes = collection_physical_attributes.find_one(
        {"username": username}, 
        {"_id": 0}  # Exclude MongoDB's `_id`
    )

    # Merge both datasets
    user_data = {
        **user,  # Include user details
        **(physical_attributes or {})  # Include attributes if found
    }
    return {"success": True, "user": user_data}

class ChatRequest(BaseModel):
    username: str
    user_input: str

class ChatResponse(BaseModel):
    response: str


def build_fallback_chat_response(user_input: str, user_profile: Optional[dict] = None) -> str:
    """Return a simple guidance response when RAG/LLM dependencies are unavailable."""
    lowered = (user_input or "").lower()
    name = (user_profile or {}).get("name")
    greeting_name = f" {name}" if name else ""

    if any(word in lowered for word in ["diet", "nutrition", "food", "meal"]):
        raw = (
            f"Hi{greeting_name}! I am running in fallback mode right now. "
            "For recovery nutrition, focus on protein in each meal, hydrate well, "
            "and include vegetables and whole grains. If you share your goals, I can suggest a sample day plan."
        )
        return _format_structured_response(raw, "nutrition")

    if any(word in lowered for word in ["pain", "knee", "back", "shoulder"]):
        raw = (
            f"Hi{greeting_name}! I am in fallback mode. "
            "For pain-related recovery, keep movements controlled, avoid sudden high intensity, "
            "and stop any exercise that causes sharp pain. I can suggest gentle low-impact options if you want."
        )
        return _format_structured_response(raw, "pain")

    if any(word in lowered for word in ["exercise", "plan", "workout"]):
        raw = (
            f"Hi{greeting_name}! I am in fallback mode at the moment. "
            "A safe starter plan is: 5-10 min warm-up, 2-3 light mobility drills, "
            "and 2 strength exercises with controlled reps. I can build a simple weekly schedule for you."
        )
        return _format_structured_response(raw, "exercise")

    raw = (
        f"Hi{greeting_name}! I am currently running in fallback mode because the advanced chatbot model "
        "is unavailable. You can still ask about exercise, pain management, or nutrition and I will help."
    )
    return _format_structured_response(raw, "general")

def fetch_document_for_user(username: str):
    document = physical_attributes_collection.find_one({"username": username})  # Query MongoDB
    #print("Fetched document:", document)  # Debugging line
    if document:
        return document
    return "No document found for this user."

def update_weeklyplan(username, query_document):
    if query_document != "Empty":
        weekly_plan_match = re.search(r"Weekly_Plan:\s*(.*)Recovery_Weeks:", query_document, re.DOTALL)
        weekly_plan_text = weekly_plan_match.group(1).strip() if weekly_plan_match else ""

        # Extract full week details
        weeks = re.findall(r"(Week \d+: .*?)(?=Week \d+:|$)", weekly_plan_text, re.DOTALL)

        # Store each full week as a dictionary
        weekly_plans = [week.strip() for week in weeks]

        # Overwrite existing document for this user
        WeeklyPlan_collection.update_one(
            {"username": username}, 
            {"$set": {"username": username, "weekly_plans": weekly_plans}}, 
            upsert=True  # Creates a new document if username doesn't exist
        )

        print("Weekly plan updated successfully for:", username)
    else: 
        print("Empty document, no updates made.")


@app.post("/chats", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    try:
        ensure_db_ready()

        username = (request.username or "").strip()
        user_input = (request.user_input or "").strip()

        if not username or not user_input:
            raise HTTPException(status_code=400, detail="Username and user_input are required.")

        cached_response = _get_cached_chat_response(username, user_input)
        if cached_response:
            return ChatResponse(response=cached_response)

        user_profile = collection_users.find_one({"username": username}, {"_id": 0, "password": 0})

        if _needs_clarification(user_input):
            clarification = _build_clarifying_prompt(user_profile)
            _set_cached_chat_response(username, user_input, clarification)
            return ChatResponse(response=clarification)

        if Ragbot is None or embedding_generator is None:
            fallback_response = build_fallback_chat_response(user_input, user_profile)
            _set_cached_chat_response(username, user_input, fallback_response)
            return ChatResponse(response=fallback_response)

        physical_attribute_document = fetch_document_for_user(username)
      

        if not physical_attribute_document:
            raise HTTPException(status_code=404, detail="No document found for this user.")
        

        #print("Query FROM Concatianted string "  , refined_query)

        query_document ,response = Ragbot.adaptive_retrieval(user_input, embedding_generator, physical_attribute_document)

        router = Ragbot.route_query(user_input)
        if router == "patient":
            update_weeklyplan(username,query_document)


        formatted = _format_structured_response(response, _detect_chat_intent(user_input))
        _set_cached_chat_response(username, user_input, formatted)
        return ChatResponse(response=formatted)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/weekly-plan/{username}")
async def get_weekly_plan(username: str):
    weekly_plan = WeeklyPlan_collection.find_one({"username": username})
    if not weekly_plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")
    
    # Convert ObjectId to string for JSON serialization
    weekly_plan["_id"] = str(weekly_plan["_id"])
    
    return weekly_plan

@app.get("/user/{username}")
async def get_user(username: str):
    # Try to find user in Users collection
    user = collection_users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user["_id"])
    
    # Get physical attributes if they exist
    physical_attributes = physical_attributes_collection.find_one({"username": username})
    if physical_attributes:
        # Convert ObjectId to string
        physical_attributes["_id"] = str(physical_attributes["_id"])
        # Merge physical attributes with user data
        user.update({k: v for k, v in physical_attributes.items() if k != "_id" and k != "username"})
    
    return user

@app.get("/vision-report/latest")
async def get_latest_vision_report():
    vision_reports_collection = db["vision_reports"]
    
    report = vision_reports_collection.find_one(
        {},  # No filter, get any document
    sort=[("timestamp", -1)]
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="No vision report found")
    
    report["_id"] = str(report["_id"])  # Serialize ObjectId
    
    return report

if __name__ == "__main__":
    print("Starting Backend server on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)