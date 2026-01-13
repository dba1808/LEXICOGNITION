"""
LexiCognition - Simple Single-Command Startup
Just run: python run.py
"""
import subprocess
import sys
import time
import os
import signal

def kill_port(port):
    """Kill any process using the specified port"""
    try:
        # Find process on port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            pids = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
            
            for pid in pids:
                subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                print(f"✅ Killed process on port {port} (PID {pid})")
    except Exception as e:
        pass

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           🎓 LexiCognition - Starting...                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Clean up old processes
    print("🧹 Cleaning up old processes...")
    kill_port(8000)
    kill_port(8501)
    time.sleep(2)
    
    # Step 2: Suppress TensorFlow warnings
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    # Step 3: Start backend in background
    print("🚀 Starting Backend (FastAPI) on port 8000...")
    backend_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'backend.main:app',
         '--host', '0.0.0.0', '--port', '8000', '--reload'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("⏳ Waiting 5 seconds for backend to initialize...")
    time.sleep(5)
    
    # Step 4: Start frontend in foreground
    print("🌐 Starting Frontend (Streamlit) on port 8501...")
    print("\n" + "="*60)
    print("✅ Services are starting!")
    print("📱 Frontend: http://localhost:8501")
    print("🔌 Backend API: http://localhost:8000")
    print("="*60 + "\n")
    print("Press Ctrl+C to stop all services.\n")
    
    try:
        # Run Streamlit in foreground so we can see the output
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'frontend/app.py',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        backend_process.terminate()
        time.sleep(2)
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()
