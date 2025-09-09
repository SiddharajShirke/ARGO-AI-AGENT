"""
Complete System Startup - HTML Frontend + FastAPI Backend
Simple startup script to run both servers
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend on port 8002...")
    try:
        subprocess.run([
            sys.executable, "-m", "app.main"
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend server error: {e}")

def start_frontend():
    """Start the HTML frontend server"""
    print("🌐 Starting HTML frontend on port 3005...")
    try:
        subprocess.run([
            sys.executable, "start_html_frontend.py"
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend server error: {e}")

def main():
    """Start both servers concurrently"""
    print("🌊 Indian Ocean ARGO AI Agent - Complete System Startup")
    print("=" * 60)
    print("Backend API: http://localhost:8002")
    print("Frontend UI: http://localhost:3005")
    print("API Docs: http://localhost:8002/api/docs")
    print("=" * 60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend a moment to start
    time.sleep(2)
    
    # Start frontend in main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested")
        print("✅ Both servers stopped")

if __name__ == "__main__":
    main()
