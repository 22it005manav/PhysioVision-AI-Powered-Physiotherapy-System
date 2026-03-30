# PhysioVision: AI-Powered Physiotherapy System

## Overview

PhysioVision is a full-stack, AI-powered physiotherapy platform that guides, monitors, and supports patients through their rehabilitation journey. It combines a modern web frontend, a robust backend with RAG-based chatbot, and a real-time computer vision system for exercise analysis.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Tech Stack](#tech-stack)
3. [Features](#features)
4. [AI & Model Details](#ai--model-details)
5. [Backend Logic](#backend-logic)
6. [Vision Backend Logic](#vision-backend-logic)
7. [Frontend Overview](#frontend-overview)
8. [Setup & Running](#setup--running)
9. [Limitations](#limitations)
10. [Project Structure](#project-structure)
11. [References & Media](#references--media)

---

## System Architecture

- **Frontend:** Next.js (React, TypeScript, Tailwind CSS)
- **API Backend:** FastAPI (Python) with MongoDB, RAG pipeline, and authentication
- **Vision Backend:** Python WebSocket server using OpenCV, MediaPipe, and ML models for real-time exercise analysis
- **Persistence:** MongoDB for user data, plans, and reports
- **Communication:** REST APIs and WebSockets

---

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Ant Design, Axios, WebSockets
- **Backend:** FastAPI, Pydantic, Uvicorn, PyMongo, SentenceTransformers, LangChain, MistralAI, Pandas, OpenPyXL
- **Vision Backend:** Python, OpenCV, MediaPipe, TensorFlow, scikit-learn, joblib, websockets, edge-tts, googletrans
- **Database:** MongoDB
- **Other:** Docker-ready, Windows batch scripts for easy startup

---

## Features

- User registration, login, and profile management
- Physical attributes and health data intake
- AI chatbot for nutrition and therapy Q&A (RAG-based, adaptive)
- Real-time posture analysis for Squats, Lunges, Warrior Pose, and Leg Raises
- Rep counting and form feedback with visual and audio (English/Urdu) cues
- Session report generation and progress tracking
- Bilingual audio feedback (Edge TTS + translation)
- Modular, multi-service architecture for easy extension

---

## AI & Model Details

### Chatbot (RAG Pipeline)

- **Embedding Model:** SentenceTransformer (all-MiniLM-L6-v2)
- **Retrieval:** Adaptive retrieval from patient and nutrition datasets (stored as .npy embeddings)
- **LLM:** MistralAI (mistral-large-latest) for response generation
- **Pipeline:** User query → intent detection → embedding → similarity search → context → LLM response

### Vision Models

- **Pose Estimation:** MediaPipe Pose (Google)
- **Squats:** Custom TensorFlow Keras model (`best_squat_model.keras`) trained on pose keypoints, with scaler and label encoder
- **Lunges:** scikit-learn model with PCA and scaler, custom logic for rep counting and form feedback
- **Warrior Pose & Leg Raises:** Rule-based analysis using pose angles and thresholds
- **Feedback:** Real-time, frame-by-frame analysis with error detection and rep counting

---

## Backend Logic

### FastAPI Backend

- **Endpoints:** Auth, user profile, health data, chat, weekly plan, vision report
- **RAG Chatbot:** Loads embeddings, routes queries, generates responses, caches frequent queries
- **MongoDB:** Stores users, physical attributes, weekly plans, and session reports
- **Security:** CORS enabled, environment variable support, plaintext password (should be hashed for production)

---

## Vision Backend Logic

- **WebSocket Server:** Receives video frames, returns annotated frames, feedback, and rep counts
- **Exercise Analyzers:**
  - **Squats:** ML model predicts form, counts reps, provides feedback
  - **Lunges:** Angle-based and ML logic, tracks leading leg, rep cycles, and common errors
  - **Warrior Pose:** Checks knee, hip, torso, and arm angles for pose correctness
  - **Leg Raises:** Monitors leg angle, hip movement, and rep quality
- **Session Reports:** Summarizes good form duration, errors, and reps at end of session
- **Audio Feedback:** Uses Edge TTS and Google Translate for bilingual support

---

## Frontend Overview

- **Pages:** Landing, Auth (Sign In/Up/Reset), Dashboard, Chatbot, Start Therapy, Contact, Profile, Exercise pages (Squats, Lunges, Warrior, Leg Raises)
- **Components:** Sidebar, User Info Form, Toggle Switch, Skeleton Camera, etc.
- **State Management:** React Context for user and audio state
- **API Integration:** Axios for REST, WebSocket for vision feedback
- **UI:** Responsive, modern, and accessible

---

## Setup & Running

### Prerequisites

- Python 3.10+
- Node.js + npm
- MongoDB running locally

### Quick Start

```bash
# Frontend
npm install
npm run dev

# Backend
cd Backend/Backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app/main.py

# Vision Backend
cd Backend_Vision
python -m venv backend_env
backend_env\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Or use the provided scripts:

- `START_ALL_SERVICES.bat` (Windows)
- `START_SERVICES.py`
- `PRE_FLIGHT_CHECK.py` (checks environment and dependencies)

---

## Limitations

- **Password Security:** Passwords are stored in plaintext (hashing required for production)
- **Port Consistency:** Some frontend calls are hardcoded to port 8000; ensure all services use the same port or update configs
- **Model Generalization:** Vision models may require further training for diverse body types and environments
- **No Mobile App:** Web-only interface
- **No Therapist Portal:** Patient-focused, but can be extended
- **No Production-Grade Auth:** No JWT/session management yet
- **Hardware Requirements:** Real-time vision requires a modern CPU and webcam

---

## Project Structure

- **Frontend:** `app/`, `components/`, `contexts/`, `utils/`
- **Backend:** `Backend/Backend/app/`
- **Vision Backend:** `Backend_Vision/`
- **Models:** `Backend_Vision/models_vision/`
- **Static Assets:** `public/`
- **Docs & Scripts:** `README.md`, `QUICK_START.md`, `SERVICE_ACCESS_GUIDE.md`, `START_ALL_SERVICES.bat`, etc.

---

## References & Media

- [Landing Page Demo](https://github.com/user-attachments/assets/cefce571-ed6c-448c-bc1d-8d76b639a029)
- [Sign Up/In Demo](https://github.com/user-attachments/assets/2420debe-f6bc-47a8-86d2-38ae03be5384)
- [Recommendation System Demo](https://github.com/user-attachments/assets/26a7f9aa-36be-4841-ab76-efeb5a698950)
- [Leg Raises Demo](https://github.com/user-attachments/assets/4bb059af-f916-4c81-af94-709af0bc35b5)
- [Lunges Demo](https://github.com/user-attachments/assets/bc35a97a-2498-49dd-b6f5-05034a9fa7fc)
- [Squats Demo](https://github.com/user-attachments/assets/959479b5-4d65-41a7-a4ec-a0675ec4de9e)
- [Warrior Pose Demo](https://github.com/user-attachments/assets/52766d32-4591-4575-a242-49d52bbdd829)
- [Audio Bot Demo](https://github.com/user-attachments/assets/e9bb517b-65ab-4906-9b2b-91700dd13d7c)
- [Complete System Demo](https://github.com/user-attachments/assets/151388e1-b676-4925-b3af-e60a923c4a18)
- [Project Poster](https://github.com/user-attachments/assets/9ecedbee-da63-4481-b94c-a2591fd09d98)

---

For any issues, see the troubleshooting section in the README or run `PRE_FLIGHT_CHECK.py`.

- Frontend: Next.js (React, TypeScript, Tailwind)
- API backend: FastAPI + MongoDB + RAG pipeline
- Vision backend: Python WebSocket server + OpenCV + MediaPipe + ML model assets

## 2. Complete repository map (what is included)

### Root files

- 000_START_HERE.md
- App.tsx
- CHANGELOG.md
- MONGODB_SETUP_GUIDE.md
- next-env.d.ts
- next.config.js
- package.json
- postcss.config.js
- PRE_FLIGHT_CHECK.py
- QUICK_START.md
- README.md
- SERVICE_ACCESS_GUIDE.md
- START_ALL_SERVICES.bat
- START_SERVICES.py
- tailwind.config.js
- test_mistral.py
- test_mongodb.py
- tsconfig.json

### Frontend app folder

- app/layout.tsx
- app/metadata.ts
- app/(auth)/layout.tsx
- app/(auth)/signin/page.tsx
- app/(auth)/signup/page.tsx
- app/(auth)/reset-password/page.tsx
- app/(default)/layout.tsx
- app/(default)/page.tsx
- app/api/auth.api.ts
- app/api/dashboard.api.ts
- app/api/userForm.api.ts
- app/chatbot/page.tsx
- app/contact/page.tsx
- app/dashboard/page.tsx
- app/frontend_vision/leg_raises/page.tsx
- app/frontend_vision/lunges_vision/page.tsx
- app/frontend_vision/squats_vision/page.tsx
- app/frontend_vision/WarriorPose/page.tsx
- app/sidebar/page.tsx
- app/start-therapy/page.tsx
- app/ToggleSwitch/page.tsx
- app/UserInfoForm/page.tsx
- app/css/style.css
- app/css/additional-styles/custom-fonts.css
- app/css/additional-styles/theme.css
- app/css/additional-styles/utility-patterns.css

### Shared frontend modules

- components/cta.tsx
- components/features.tsx
- components/hero-home.tsx
- components/modal-video.tsx
- components/page-illustration.tsx
- components/spotlight.tsx
- components/testimonials.tsx
- components/workflows.tsx
- components/ui/footer.tsx
- components/ui/header.tsx
- components/ui/logo.tsx
- contexts/AppContext.tsx
- contexts/AudioContexts.tsx
- utils/api.service.ts
- utils/useMasonry.tsx
- utils/useMousePosition.tsx

### API backend folder

- Backend/Backend/requirements.txt
- Backend/Backend/setup_database.py
- Backend/Backend/app/**init**.py
- Backend/Backend/app/chatbot.py
- Backend/Backend/app/main.py
- Backend/Backend/app/Database/fallback_db.json
- Backend/Backend/app/Database/nutrition_documents.npy
- Backend/Backend/app/Database/nutrition_embeddings.npy
- Backend/Backend/app/Database/patient_documents.npy
- Backend/Backend/app/Database/patient_embeddings.npy

### Vision backend folder

- Backend_Vision/main.py
- Backend_Vision/squats.py
- Backend_Vision/lunges_vision.py
- Backend_Vision/lunges_vision_main.py
- Backend_Vision/WarriorPose.py
- Backend_Vision/legRaises.py
- Backend_Vision/bark_tts.py
- Backend_Vision/requirements.txt
- Backend_Vision/report.txt
- Backend_Vision/models_vision/best_squat_model.keras
- Backend_Vision/models_vision/preprocessed_data_label_encoder.joblib
- Backend_Vision/models_vision/preprocessed_data_scaler.joblib

### Additional backend (legacy auth service)

- login_backend/main.py
- login_backend/requirements.txt

### Static assets

- public/fonts/
- public/images/
- public/videos/

## 3. Frontend routes and pages

### App routes

- / -> app/(default)/page.tsx (marketing landing page)
- /signin -> app/(auth)/signin/page.tsx
- /signup -> app/(auth)/signup/page.tsx
- /reset-password -> app/(auth)/reset-password/page.tsx
- /dashboard -> app/dashboard/page.tsx
- /chatbot -> app/chatbot/page.tsx
- /start-therapy -> app/start-therapy/page.tsx
- /contact -> app/contact/page.tsx
- /sidebar -> app/sidebar/page.tsx
- /UserInfoForm -> app/UserInfoForm/page.tsx
- /ToggleSwitch -> app/ToggleSwitch/page.tsx
- /frontend_vision/squats_vision -> app/frontend_vision/squats_vision/page.tsx
- /frontend_vision/lunges_vision -> app/frontend_vision/lunges_vision/page.tsx
- /frontend_vision/WarriorPose -> app/frontend_vision/WarriorPose/page.tsx
- /frontend_vision/leg_raises -> app/frontend_vision/leg_raises/page.tsx

### Frontend state/context

- AppContext: stores username in React context + localStorage
- AudioContext: stores audiobot state and selected language in localStorage

### Frontend API utilities

- utils/api.service.ts creates axios client using NEXT_PUBLIC_API_URL
- app/api/auth.api.ts wraps login call to /api/signin
- app/api/dashboard.api.ts fetches /api/user/:username
- app/api/userForm.api.ts sends profile updates to /update-field

## 4. Backend API services and endpoints

There are two FastAPI backends in this repository.

### Primary backend: Backend/Backend/app/main.py

Default run target in scripts and docs is this service.

#### Main responsibilities

- MongoDB startup connection
- User sign up and sign in
- User physical attributes upsert
- Chat endpoint using RAG class
- Weekly plan extraction/storage
- User aggregation endpoint for dashboard
- Latest vision report retrieval endpoint

#### Endpoints

- POST /api/signup
- POST /api/signin
- POST /update-field
- GET /api/user/{username}
- POST /chats
- GET /weekly-plan/{username}
- GET /user/{username}
- GET /vision-report/latest

#### Data collections used

- PhysioVision.Users
- PhysioVision.User_PhysicalAttributes
- PhysioVision.User_WeeklyPlan
- PhysioVision.vision_reports (read for latest report)

### Legacy auth backend: login_backend/main.py

This is a separate FastAPI service with overlapping auth endpoints.

#### Endpoints

- POST /api/signup
- POST /api/signin
- GET /api/user/{username}
- POST /submit_physical_attributes

## 5. RAG module details

Implemented in Backend/Backend/app/chatbot.py.

### Components

- EmbeddingGenerator (SentenceTransformer all-MiniLM-L6-v2)
- RAG class for:
  - dataset loading from .npy embeddings/documents
  - route_query (nutrition vs patient query routing)
  - adaptive_retrieval
  - response generation through Mistral client

### RAG data files included

- patient_embeddings.npy
- patient_documents.npy
- nutrition_embeddings.npy
- nutrition_documents.npy

## 6. Vision backend details

Implemented in Backend_Vision/main.py.

### Transport

- WebSocket server on ws://localhost:8765

### Supported exercises (keys)

- Squats
- Lunges
- Warrior
- LegRaises

### Client actions handled

- connect
- start
- stop
- disconnect

### Vision analyzers

- SquatAnalyzer (Backend_Vision/squats.py)
- LungesAnalyzer (Backend_Vision/lunges_vision.py)
- WarriorPoseAnalyzer (Backend_Vision/WarriorPose.py)
- SLRExerciseAnalyzer (Backend_Vision/legRaises.py)

### Session outputs

- Streaming frame payloads (base64 image frames + counters/feedback)
- error_text for voice feedback pipeline
- End-of-session textual report written to Backend_Vision/report.txt

### TTS and translation

- Backend_Vision/bark_tts.py uses edge_tts
- Urdu translation via googletrans
- Audio returned as base64 and broadcast to clients

## 7. Dependencies included

### Frontend (package.json)

- next, react, react-dom, typescript
- tailwindcss, postcss, autoprefixer
- axios
- antd, @ant-design/icons
- framer-motion, lucide-react, react-icons
- socket.io-client
- react-datepicker
- emailjs-com
- aos

### API backend (Backend/Backend/requirements.txt)

- fastapi, uvicorn
- pymongo
- sentence-transformers, numpy, scikit-learn
- langchain and related packages
- mistralai, tiktoken
- pandas, openpyxl

### Vision backend (Backend_Vision/requirements.txt)

- opencv-python, mediapipe
- tensorflow, scikit-learn, scipy, numpy, pandas, joblib
- fastapi, uvicorn, websockets
- edge_tts
- googletrans==3.1.0a0

### Legacy auth backend (login_backend/requirements.txt)

- fastapi, uvicorn, pymongo, pydantic

## 8. Setup and run instructions

## Prerequisites

- Python 3.10+ recommended for vision stack compatibility
- Node.js + npm
- MongoDB running locally on localhost:27017 (or update connection string)

## Frontend

```bash
npm install
npm run dev
```

## Primary backend

```bash
cd Backend/Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

## Vision backend

```bash
cd Backend_Vision
python -m venv backend_env
backend_env\Scripts\activate
pip install -r requirements.txt
python main.py
```

## One-command helpers included in repo

- START_SERVICES.py
- START_ALL_SERVICES.bat
- PRE_FLIGHT_CHECK.py

Typical startup flow used by helper scripts:

- Checks MongoDB
- Starts backend service
- Starts frontend dev server

## 9. Important integration notes (current code behavior)

This section is important for avoiding runtime confusion.

### Port usage is mixed in frontend code

- Some frontend files call http://localhost:8000 directly (for example dashboard/chatbot/signup)
- Utility axios client is configured from NEXT_PUBLIC_API_URL (often set to http://localhost:8002)
- START_SERVICES.py starts backend on port 8002

Result: if only the 8002 backend is running, pages hardcoded to 8000 will fail unless updated.

### Suggested local alignment

Use one backend port consistently across all frontend calls (either 8000 or 8002) and set NEXT_PUBLIC_API_URL to the same value.

## 10. Data and persistence

### MongoDB database

- Database: PhysioVision
- Core collections:
  - Users
  - User_PhysicalAttributes
  - User_WeeklyPlan

### Setup helper

Backend/Backend/setup_database.py can initialize fallback files and dummy embedding files.

## 11. Test and utility scripts

- PRE_FLIGHT_CHECK.py: validates environment, ports, files, dependencies
- START_SERVICES.py: starts services and prints access URLs
- START_ALL_SERVICES.bat: Windows multi-terminal launcher
- test_mongodb.py: checks MongoDB connectivity
- test_mistral.py: checks Mistral-related behavior

## 12. Other documentation included

- QUICK_START.md
- SERVICE_ACCESS_GUIDE.md
- MONGODB_SETUP_GUIDE.md
- 000_START_HERE.md
- CHANGELOG.md

## 13. Security and production notes

Before production deployment:

- Remove hardcoded secrets and API keys from source
- Move DB URI and API keys to environment variables
- Add password hashing for auth flow (current code compares plaintext)
- Restrict CORS origins appropriately
- Add proper auth tokens/session management

## 14. Media/demo references

The following presentation assets are currently referenced in this project:

- Landing page demo:
  - https://github.com/user-attachments/assets/cefce571-ed6c-448c-bc1d-8d76b639a029
- Sign up / sign in / forgot password demo:
  - https://github.com/user-attachments/assets/2420debe-f6bc-47a8-86d2-38ae03be5384
- Recommendation system demo:
  - https://github.com/user-attachments/assets/26a7f9aa-36be-4841-ab76-efeb5a698950
- Leg raises demo:
  - https://github.com/user-attachments/assets/4bb059af-f916-4c81-af94-709af0bc35b5
- Lunges demo:
  - https://github.com/user-attachments/assets/bc35a97a-2498-49dd-b6f5-05034a9fa7fc
- Squats demo:
  - https://github.com/user-attachments/assets/959479b5-4d65-41a7-a4ec-a0675ec4de9e
- Warrior pose demo:
  - https://github.com/user-attachments/assets/52766d32-4591-4575-a242-49d52bbdd829
- Audio bot demo:
  - https://github.com/user-attachments/assets/e9bb517b-65ab-4906-9b2b-91700dd13d7c
- Complete system demo:
  - https://github.com/user-attachments/assets/151388e1-b676-4925-b3af-e60a923c4a18
- Project poster:
  - https://github.com/user-attachments/assets/9ecedbee-da63-4481-b94c-a2591fd09d98

## 15. Quick access summary

Typical local URLs:

- Frontend: http://localhost:3000 or http://localhost:3001 (depends on port availability)
- Backend API docs (primary): http://localhost:8002/docs
- Backend API docs (legacy): http://localhost:8000/docs
- Vision WebSocket: ws://localhost:8765

If something does not connect, check Section 9 first (port alignment) and then run PRE_FLIGHT_CHECK.py.
