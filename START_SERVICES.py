#!/usr/bin/env python3
"""
PhysioVision Complete Service Manager
Starts and manages all services (Backend, Frontend, MongoDB)
"""

import subprocess
import time
import os
import sys
import signal
import socket
import shutil
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

class ServiceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "Backend" / "Backend"
        self.vision_path = self.project_root / "Backend_Vision"
        self.frontend_path = self.project_root
        self.backend_python = self.backend_path / "venv" / "Scripts" / "python.exe"
        self.vision_python_310 = self.vision_path / "backend_env_310" / "Scripts" / "python.exe"
        self.vision_python = self.vision_path / "venv" / "Scripts" / "python.exe"
        self.processes = []

    def _wait_for_url(self, url: str, timeout_seconds: int = 20) -> bool:
        """Wait until an HTTP endpoint becomes reachable."""
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            try:
                with urlopen(url, timeout=2):
                    return True
            except URLError:
                time.sleep(1)
            except Exception:
                time.sleep(1)
        return False

    def _wait_for_tcp_port(self, host: str, port: int, timeout_seconds: int = 20) -> bool:
        """Wait until a TCP port is accepting connections."""
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                sock.connect((host, port))
                sock.close()
                return True
            except Exception:
                time.sleep(1)
            finally:
                try:
                    sock.close()
                except Exception:
                    pass
        return False

    def _resolve_vision_python(self) -> str:
        """Resolve the best Python executable for the vision backend."""
        if self.vision_python_310.exists():
            return str(self.vision_python_310)
        if self.vision_python.exists():
            return str(self.vision_python)
        return sys.executable
        
    def check_mongodb(self):
        """Check if MongoDB is running"""
        print("\n🧪 Checking MongoDB Connection...")
        print("-" * 70)
        
        try:
            # Use a lightweight TCP check so START_SERVICES.py works even when
            # this interpreter does not have pymongo installed.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect(("localhost", 27017))
            sock.close()
            print("✅ MongoDB port is reachable on localhost:27017")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB is NOT running: {e}")
            print("\n   💡 To start MongoDB:")
            print("      Windows: Download from https://www.mongodb.com/try/download/community")
            print("      Then: Open Services (services.msc) and start 'MongoDB'")
            return False

    def start_backend(self):
        """Start FastAPI backend server"""
        print("\n🚀 Starting Backend API Server...")
        print("-" * 70)
        
        try:
            # Change to Backend directory
            os.chdir(self.backend_path)

            python_executable = (
                str(self.backend_python)
                if self.backend_python.exists()
                else sys.executable
            )
            
            # Start backend directly via app/main.py for stable startup on Windows.
            cmd = [
                python_executable,
                "app/main.py"
            ]
            
            print(f"📁 Working directory: {os.getcwd()}")
            print(f"▶️  Command: {' '.join(cmd)}")
            print("\nBackend output:")
            print("-" * 70)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={
                    **os.environ,
                    "PYTHONUTF8": "1",
                    "PYTHONIOENCODING": "utf-8"
                }
            )
            
            self.processes.append(("Backend", process))

            # If process exits quickly, surface the error immediately.
            try:
                process.wait(timeout=4)
                output = process.stdout.read() if process.stdout else ""
                if output:
                    print(output.rstrip())
                print("-" * 70)
                print(f"❌ Backend exited early with code {process.returncode}")
                return False
            except subprocess.TimeoutExpired:
                pass

            if not self._wait_for_url("http://localhost:8002/docs", timeout_seconds=45):
                print("-" * 70)
                print("❌ Backend did not become reachable at http://localhost:8002/docs")
                return False
            
            print("-" * 70)
            print("✅ Backend started (output continues in background)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False

    def start_frontend(self):
        """Start Next.js frontend"""
        print("\n🌐 Starting Frontend Dev Server...")
        print("-" * 70)
        
        try:
            os.chdir(self.frontend_path)
            
            # Use npm.cmd explicitly for Windows subprocess compatibility.
            npm_cmd = shutil.which("npm.cmd") or shutil.which("npm") or "npm"
            cmd = [npm_cmd, "run", "dev", "--", "-p", "3001"]
            
            print(f"📁 Working directory: {os.getcwd()}")
            print(f"▶️  Command: {' '.join(cmd)}")
            print("\nFrontend output:")
            print("-" * 70)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.processes.append(("Frontend", process))

            try:
                process.wait(timeout=4)
                output = process.stdout.read() if process.stdout else ""
                if output:
                    print(output.rstrip())
                print("-" * 70)
                print(f"❌ Frontend exited early with code {process.returncode}")
                return False
            except subprocess.TimeoutExpired:
                pass

            if not self._wait_for_url("http://localhost:3001", timeout_seconds=30):
                print("-" * 70)
                print("❌ Frontend did not become reachable at http://localhost:3001")
                return False
            
            print("-" * 70)
            print("✅ Frontend started (output continues in background)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False

    def start_vision_backend(self):
        """Start Vision WebSocket backend server"""
        print("\n🎥 Starting Vision WebSocket Server...")
        print("-" * 70)

        try:
            os.chdir(self.vision_path)

            python_executable = self._resolve_vision_python()
            cmd = [python_executable, "main.py"]

            print(f"📁 Working directory: {os.getcwd()}")
            print(f"▶️  Command: {' '.join(cmd)}")
            print("\nVision backend output:")
            print("-" * 70)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={
                    **os.environ,
                    "PYTHONUTF8": "1",
                    "PYTHONIOENCODING": "utf-8"
                }
            )

            self.processes.append(("Vision Backend", process))

            try:
                process.wait(timeout=8)
                output = process.stdout.read() if process.stdout else ""
                if output:
                    print(output.rstrip())
                print("-" * 70)
                print(f"❌ Vision backend exited early with code {process.returncode}")
                if "module 'mediapipe' has no attribute 'solutions'" in output:
                    print("\n💡 MediaPipe compatibility issue detected.")
                    print("   This project's vision analyzers require the legacy pose API (mp.solutions).")
                    print("   Create a Python 3.10 env at Backend_Vision\\backend_env_310 and install requirements there.")
                return False
            except subprocess.TimeoutExpired:
                pass

            if not self._wait_for_tcp_port("localhost", 8765, timeout_seconds=25):
                print("-" * 70)
                print("❌ Vision backend did not become reachable on ws://localhost:8765")
                return False

            print("-" * 70)
            print("✅ Vision backend started (output continues in background)")
            return True

        except Exception as e:
            print(f"❌ Failed to start vision backend: {e}")
            return False

    def show_services_info(self):
        """Display all services information"""
        print("\n" + "=" * 70)
        print("✨ ALL SERVICES STARTED SUCCESSFULLY!")
        print("=" * 70)
        
        print("\n📍 ACCESS YOUR SERVICES:\n")
        
        services = [
            ("🌐 Frontend UI", "http://localhost:3001", "Login/Register here"),
            ("🔵 Backend API", "http://localhost:8002", "RESTful API server"),
            ("📚 API Documentation", "http://localhost:8002/docs", "Swagger UI - test endpoints"),
            ("🎥 Vision WebSocket", "ws://localhost:8765", "Exercise detection stream"),
            ("🗄️  MongoDB", "localhost:27017", "Database connection"),
        ]
        
        for title, url, desc in services:
            print(f"{title:25} {url:30} ({desc})")
        
        print("\n" + "-" * 70)
        print("🧪 TEST AUTHENTICATION:\n")
        
        print("1️⃣  SIGN UP (Register New User):")
        print("   - Go to http://localhost:3001/signup")
        print("   - Fill in: Name, Username, Email, Password")
        print("   - Click Register\n")
        
        print("2️⃣  SIGN IN (Login):")
        print("   - Go to http://localhost:3001/signin")
        print("   - Enter Username and Password you just created")
        print("   - Click Sign In\n")
        
        print("3️⃣  TEST WITH API DOCS:")
        print("   - Go to http://localhost:8002/docs")
        print("   - Try POST /api/signup")
        print("   - Try POST /api/signin")
        print("   - Check response messages")
        
        print("\n" + "-" * 70)
        print("📊 AVAILABLE FEATURES:\n")
        
        features = [
            ("Authentication", "/api/signup, /api/signin"),
            ("User Profile", "/api/user/{username}"),
            ("Health Data", "/update-field"),
            ("Chatbot/RAG", "Integration ready"),
            ("Exercise Analysis", "Vision module ready"),
        ]
        
        for feature, endpoint in features:
            print(f"  ✅ {feature:20} {endpoint}")
        
        print("\n" + "=" * 70)
        print("💡 KEYBOARD SHORTCUTS:\n")
        print("  Ctrl+C   - Stop all services")
        print("  Ctrl+Z   - Pause services (Ctrl+C again to resume)")
        print("\n" + "=" * 70 + "\n")

    def run(self):
        """Run all services"""
        print("\n" + "=" * 70)
        print("🎯 PhysioVision Complete Service Manager")
        print("=" * 70)
        
        # Check MongoDB first
        if not self.check_mongodb():
            print("\n⚠️  MongoDB check failed. Backend might not work properly, continuing startup...")
        
        # Start Backend
        if not self.start_backend():
            print("⚠️  Backend startup had issues but will continue...")
        
        time.sleep(3)
        
        # Start Frontend
        if not self.start_frontend():
            print("⚠️  Frontend startup had issues but will continue...")

        time.sleep(2)

        # Start Vision Backend
        if not self.start_vision_backend():
            print("⚠️  Vision backend startup had issues. Exercise pages may show disconnected status.")
        
        time.sleep(3)
        
        # Show service info
        self.show_services_info()
        
        # Keep services running
        try:
            print("⏱️  Services are running. Press Ctrl+C to stop all services...\n")
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"\n⚠️  {name} process ended with code {process.returncode}")
                        
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping all services...")
            self.stop_all()

    def stop_all(self):
        """Stop all processes"""
        for name, process in self.processes:
            print(f"  Stopping {name}...", end=" ")
            try:
                process.terminate()
                process.wait(timeout=5)
                print("✅")
            except subprocess.TimeoutExpired:
                print("Force stopping...", end=" ")
                process.kill()
                print("✅")
            except Exception as e:
                print(f"❌ ({e})")
        
        print("\n✨ All services stopped. Thank you for using PhysioVision!")

def main():
    """Main entry point"""
    manager = ServiceManager()
    
    # Handle signals
    def signal_handler(sig, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run services
    manager.run()

if __name__ == "__main__":
    main()
