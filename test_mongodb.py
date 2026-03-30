#!/usr/bin/env python3
"""
PhysioVision MongoDB Connection Tester
Tests MongoDB connection and provides setup guidance
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import time

def test_mongodb():
    """Test MongoDB connection and display status"""
    
    print("\n" + "="*70)
    print("🧪 PhysioVision MongoDB Connection Tester")
    print("="*70 + "\n")
    
    # Test local MongoDB
    print("Testing LOCAL MongoDB (localhost:27017)...")
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ LOCAL MongoDB is RUNNING!\n")
        
        # List databases
        db_list = client.list_database_names()
        print(f"✅ Databases found: {db_list if db_list else 'None yet'}")
        
        # Try to create PhysioVision DB
        db = client["PhysioVision"]
        print(f"✅ PhysioVision database accessible")
        
        # Create collections if they don't exist
        collections = ["Users", "User_PhysicalAttributes", "User_WeeklyPlan"]
        for col in collections:
            if col not in db.list_collection_names():
                db[col].insert_one({"_init": True})
                db[col].delete_one({"_init": True})
                print(f"   ✅ Created collection: {col}")
            else:
                print(f"   ✅ Collection exists: {col}")
        
        return True
        
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print(f"❌ LOCAL MongoDB is NOT running\n")
        print(f"   Error: {e}\n")
        return False

def show_setup_options():
    """Display MongoDB setup options"""
    
    print("\n" + "-"*70)
    print("📋 How to Set Up MongoDB")
    print("-"*70 + "\n")
    
    print("OPTION 1: MongoDB Atlas (Cloud - RECOMMENDED)")
    print("  - Go to: https://www.mongodb.com/cloud/atlas")
    print("  - Create FREE cluster (M0)")
    print("  - Get connection string")
    print("  - Update: Backend/Backend/app/main.py (line with 'uri =')")
    print("  ⏱️  Takes: 5-10 minutes\n")
    
    print("OPTION 2: Local MongoDB (Windows)")
    print("  - Download: https://www.mongodb.com/try/download/community")
    print("  - Run installer (.msi)")
    print("  - MongoDB auto-starts on localhost:27017")
    print("  - Already configured in Backend!")
    print("  ⏱️  Takes: 5-10 minutes\n")
    
    print("OPTION 3: Docker (if installed)")
    print("  - Run: docker run -d -p 27017:27017 mongo:latest")
    print("  - Already configured in Backend!")
    print("  ⏱️  Takes: 1 minute\n")

def main():
    """Main test function"""
    
    # Test local MongoDB
    is_connected = test_mongodb()
    
    if not is_connected:
        show_setup_options()
        print("\n" + "="*70)
        print("⚠️  MongoDB is not available, but the backend can still run!")
        print("    - RAG system will work in demo mode")
        print("    - User database operations will be limited")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("✨ Everything is ready! You can now run:")
        print("-"*70)
        print("Terminal 1 - Backend:")
        print("  cd Backend\\Backend")
        print("  .\\venv\\Scripts\\python app\\main.py\n")
        print("Terminal 2 - Frontend:")
        print("  npm run dev")
        print("="*70 + "\n")

if __name__ == "__main__":
    main()
