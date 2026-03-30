#!/usr/bin/env python3
"""
PhysioVision Pre-Flight Check
Verifies all systems are ready before starting services
"""

import sys
import os
import subprocess
from pathlib import Path

class PreFlightCheck:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.all_good = True
        self.checks = []
        
    def check(self, name, condition, error_msg=""):
        """Track a check result"""
        status = "✅" if condition else "❌"
        self.checks.append((name, condition, error_msg))
        print(f"{status} {name}", end="")
        if not condition:
            self.all_good = False
            if error_msg:
                print(f" - {error_msg}")
            else:
                print()
        else:
            print()
    
    def run_all_checks(self):
        """Run all pre-flight checks"""
        print("\n" + "=" * 70)
        print("🚀 PhysioVision Pre-Flight Check")
        print("=" * 70 + "\n")
        
        # 1. Check project structure
        print("📁 Checking Project Structure...")
        print("-" * 70)
        
        self.check("Backend folder exists", 
                   (self.project_root / "Backend" / "Backend").exists())
        self.check("Frontend folder exists", 
                   self.project_root.exists())
        self.check("package.json exists", 
                   (self.project_root / "package.json").exists())
        self.check("Backend main.py exists", 
                   (self.project_root / "Backend" / "Backend" / "app" / "main.py").exists())
        
        # 2. Check environment files
        print("\n⚙️  Checking Environment Configuration...")
        print("-" * 70)
        
        env_local = self.project_root / ".env.local"
        self.check(".env.local exists", env_local.exists())
        
        if env_local.exists():
            content = env_local.read_text()
            self.check("NEXT_PUBLIC_API_URL configured", 
                      "NEXT_PUBLIC_API_URL" in content,
                      "Add: NEXT_PUBLIC_API_URL=http://localhost:8002")
        
        # 3. Check Python/Node installation
        print("\n🐍 Checking Python Installation...")
        print("-" * 70)
        
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            python_version = result.stdout.strip()
            self.check(f"Python installed ({python_version})", True)
        except:
            self.check("Python installed", False, "Python not in PATH")
        
        print("\n📦 Checking Node.js Installation...")
        print("-" * 70)
        
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            node_version = result.stdout.strip()
            self.check(f"Node.js installed ({node_version})", True)
        except:
            self.check("Node.js installed", False, "Node not in PATH")
        
        try:
            result = subprocess.run(["npm", "--version"], 
                                  capture_output=True, text=True)
            npm_version = result.stdout.strip()
            self.check(f"npm installed ({npm_version})", True)
        except:
            self.check("npm installed", False, "npm not in PATH")
        
        # 4. Check virtual environment
        print("\n🔧 Checking Python Virtual Environment...")
        print("-" * 70)
        
        venv_path = self.project_root / "Backend" / "Backend" / "venv"
        self.check("Backend venv exists", venv_path.exists(),
                  "Run: cd Backend\\Backend && python -m venv venv")
        
        if venv_path.exists():
            python_exe = venv_path / "Scripts" / "python.exe"
            self.check("Python executable in venv", python_exe.exists())
        
        # 5. Check MongoDB
        print("\n🗄️  Checking MongoDB...")
        print("-" * 70)
        
        try:
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017", 
                               serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            self.check("MongoDB Running", True)
            
            # Check database
            db = client["PhysioVision"]
            collections = db.list_collection_names()
            self.check("PhysioVision database exists", 
                      len(collections) > 0,
                      "Will be created on first run")
            client.close()
        except Exception as e:
            self.check("MongoDB Running", False,
                      "Start MongoDB: sc start MongoDB")
        
        # 6. Check required Python packages
        print("\n📚 Checking Python Packages...")
        print("-" * 70)
        
        packages = ["fastapi", "uvicorn", "pymongo", "sentence_transformers"]
        
        try:
            # Get list of installed packages
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True, text=True
            )
            installed = result.stdout.lower()
            
            for pkg in packages:
                self.check(f"  {pkg} installed", 
                          pkg in installed)
        except:
            print("⚠️  Could not check installed packages")
        
        # 7. Check npm packages
        print("\n📦 Checking Node Packages...")
        print("-" * 70)
        
        node_modules = self.project_root / "node_modules"
        self.check("node_modules exists", 
                  node_modules.exists(),
                  "Run: npm install")
        
        # 8. Check ports
        print("\n🔌 Checking Ports...")
        print("-" * 70)
        
        try:
            result = subprocess.run(["netstat", "-ano"], 
                                  capture_output=True, text=True)
            netstat_output = result.stdout
            
            port_3001_used = ":3001" in netstat_output
            port_8002_used = ":8002" in netstat_output
            port_27017_used = ":27017" in netstat_output
            
            self.check("Port 3001 available", 
                      not port_3001_used,
                      "Another service is using port 3001")
            self.check("Port 8002 available", 
                      not port_8002_used,
                      "Another service is using port 8002")
            self.check("Port 27017 available (MongoDB)", 
                      not port_27017_used,
                      "MongoDB might not be running")
        except:
            print("⚠️  Could not check ports")
        
        # Final summary
        print("\n" + "=" * 70)
        if self.all_good:
            print("✨ ALL CHECKS PASSED!")
            print("=" * 70)
            print("\n🚀 Ready to start services!\n")
            print("Run: python START_SERVICES.py\n")
            return True
        else:
            print("⚠️  SOME CHECKS FAILED")
            print("=" * 70)
            print("\n❌ Please fix the issues above before starting services.\n")
            print("Common fixes:")
            print("  1. Install MongoDB: https://www.mongodb.com/try/download/community")
            print("  2. Install Node.js: https://nodejs.org/")
            print("  3. Run: npm install (in project root)")
            print("  4. Run: pip install -r requirements.txt (in Backend\\Backend)")
            print()
            return False

def main():
    """Main entry point"""
    checker = PreFlightCheck()
    success = checker.run_all_checks()
    
    if not success:
        input("Press Enter to continue anyway...")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
