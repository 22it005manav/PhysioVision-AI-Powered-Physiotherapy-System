#!/usr/bin/env python3
"""
Database Setup Script for PhysioVision
This script initializes all necessary database files and structures
"""

import os
import numpy as np
import json
from pathlib import Path

def setup_rag_embeddings():
    """Create dummy RAG embedding files"""
    db_path = Path(__file__).parent / "app" / "Database"
    db_path.mkdir(exist_ok=True)
    
    print("📁 Setting up RAG Database files...")
    
    # Create empty embeddings (384-dimensional for all-MiniLM-L6-v2)
    embedding_dim = 384
    
    # Create dummy patient embeddings and documents
    patient_embeddings = np.array([[0.0] * embedding_dim])  # 1 dummy embedding
    patient_documents = np.array(["Sample patient data"], dtype=object)
    
    # Create dummy nutrition embeddings and documents
    nutrition_embeddings = np.array([[0.0] * embedding_dim])  # 1 dummy embedding
    nutrition_documents = np.array(["Sample nutrition data"], dtype=object)
    
    # Save embeddings
    np.save(db_path / "patient_embeddings.npy", patient_embeddings)
    np.save(db_path / "patient_documents.npy", patient_documents)
    np.save(db_path / "nutrition_embeddings.npy", nutrition_embeddings)
    np.save(db_path / "nutrition_documents.npy", nutrition_documents)
    
    print(f"✅ RAG embeddings created at: {db_path}")

def setup_mongodb_fallback():
    """Create fallback JSON database structure"""
    db_fallback_path = Path(__file__).parent / "app" / "Database" / "fallback_db.json"
    
    fallback_data = {
        "Users": [],
        "User_PhysicalAttributes": [],
        "User_WeeklyPlan": [],
        "ChatHistory": []
    }
    
    with open(db_fallback_path, 'w') as f:
        json.dump(fallback_data, f, indent=2)
    
    print(f"✅ Fallback JSON database created: {db_fallback_path}")

def print_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("🎯 MONGODB SETUP INSTRUCTIONS")
    print("="*60)
    print("\n📌 OPTION 1: Use Local MongoDB (Windows)")
    print("-" * 60)
    print("1. Download MongoDB from: https://www.mongodb.com/try/download/community")
    print("2. Run the installer and follow the setup wizard")
    print("3. MongoDB will start automatically on localhost:27017")
    print("4. Verify: mongosh (should connect successfully)")
    
    print("\n📌 OPTION 2: Download MongoDB Compass (GUI)")
    print("-" * 60)
    print("1. Download from: https://www.mongodb.com/products/compass")
    print("2. Install and launch MongoDB Compass")
    print("3. Connect to: mongodb://localhost:27017")
    print("4. Create database 'PhysioVision'")
    print("5. Create collections: Users, User_PhysicalAttributes, User_WeeklyPlan")
    
    print("\n📌 OPTION 3: Use Docker (if Docker Desktop is installed)")
    print("-" * 60)
    print("Run: docker run -d -p 27017:27017 --name physiovision-mongo mongo:latest")
    
    print("\n📌 OPTION 4: Use MongoDB Atlas (Cloud - Recommended for Production)")
    print("-" * 60)
    print("1. Go to: https://www.mongodb.com/cloud/atlas")
    print("2. Create a FREE cluster")
    print("3. Get connection string and update in main.py")
    print("4. Whitelist your IP address in Atlas settings")
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n🚀 PhysioVision Database Setup Started...\n")
    
    try:
        setup_rag_embeddings()
        setup_mongodb_fallback()
        print_instructions()
        print("✨ All databases initialized! Ready to run the project.\n")
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
