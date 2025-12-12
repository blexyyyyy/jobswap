import subprocess
import time
import sys
import os

def run_services():
    """
    Runs both the FastAPI backend and the Vite frontend concurrently.
    """
    processes = []
    
    try:
        # Start Backend
        print("🚀 Starting Backend (FastAPI)...")
        # Using sys.executable ensures we use the same python interpreter (venv)
        backend = subprocess.Popen(
            [sys.executable, "-m", "app.main"], 
            cwd=os.getcwd()
        )
        processes.append(backend)

        # Start Frontend
        print("🚀 Starting Frontend (Vite)...")
        # shell=True is often needed for npm on Windows to resolve the command
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        frontend = subprocess.Popen(
            ["npm", "run", "dev"], 
            cwd=frontend_dir,
            shell=True
        )
        processes.append(frontend)

        print("\n✅ Services started! Press Ctrl+C to stop.\n")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if any process has exited unexpectedly
            if backend.poll() is not None:
                print(f"❌ Backend process exited with code {backend.returncode}")
                break
            if frontend.poll() is not None:
                print(f"❌ Frontend process exited with code {frontend.returncode}")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
    finally:
        # Terminate all started processes
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    p.kill()

if __name__ == "__main__":
    run_services()
