# Script to insert sample data for weekly plan and vision report
# Run this with your backend MongoDB running

from pymongo import MongoClient
from datetime import datetime

# Update this if your MongoDB URI is different
MONGODB_URI = "mongodb://localhost:27017/PhysioVision"

client = MongoClient(MONGODB_URI)
db = client["PhysioVision"]

# Insert sample weekly plan for user 'Manav'
weekly_plan = {
    "username": "Manav",
    "weekly_plans": [
        "Week 1: 5-10 min warm-up, 2-3 light mobility drills, 2 strength exercises with controlled reps.",
        "Week 2: Increase intensity slightly, add 1 more exercise, focus on form.",
        "Week 3: Add balance drills, maintain previous routine.",
        "Week 4: Review progress, adjust based on fatigue/pain."
    ]
}
db["User_WeeklyPlan"].update_one({"username": "Manav"}, {"$set": weekly_plan}, upsert=True)
print("Inserted/updated weekly plan for Manav.")

# Insert sample vision report
db["vision_reports"].insert_one({
    "username": "Manav",
    "report": "Squat form improved. Knee alignment good. Continue current plan.",
    "timestamp": datetime.utcnow()
})
print("Inserted sample vision report.")
