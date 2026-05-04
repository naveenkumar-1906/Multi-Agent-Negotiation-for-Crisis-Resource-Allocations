#!/usr/bin/env python3
"""
Combined server that serves both frontend and backend to avoid CORS issues
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Activate virtual environment and start backend
    venv_python = Path(__file__).parent / "venv" / "bin" / "python3"
    subprocess.run([str(venv_python), "main.py"])

def start_frontend():
    """Start the frontend server"""
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Start Python HTTP server for frontend
    subprocess.run([sys.executable, "-m", "http.server", "3002"])

if __name__ == "__main__":
    print("🚀 Starting Crisis Resource Allocation System...")
    print("📊 Backend: http://localhost:8000")
    print("🌐 Frontend: http://localhost:3002")
    print("✅ Combined server starting...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in main thread
    start_frontend()
