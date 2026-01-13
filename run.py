"""
ORION - AI Viva Voce System
===========================
One-command setup and run script.

Just run: python run.py

This will automatically:
1. Create virtual environment (if not exists)
2. Install all dependencies
3. Set up the database
4. Start the application
"""
import subprocess
import sys
import os
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗                  ║
    ║    ██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║                  ║
    ║    ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║                  ║
    ║    ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║                  ║
    ║    ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║                  ║
    ║     ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝                  ║
    ║                                                              ║
    ║            🎓 AI Viva Voce Examination System                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
{Colors.END}""")

def run_command(cmd, description, cwd=None, shell=True):
    """Run a command and show status"""
    print(f"{Colors.YELLOW}⏳ {description}...{Colors.END}")
    try:
        result = subprocess.run(
            cmd, 
            shell=shell, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {description} - Done{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Error: {result.stderr[:200]}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {str(e)}{Colors.END}")
        return False

def get_venv_python():
    """Get the path to the virtual environment Python"""
    if sys.platform == "win32":
        return str(Path(".venv") / "Scripts" / "python.exe")
    else:
        return str(Path(".venv") / "bin" / "python")

def get_venv_pip():
    """Get the path to the virtual environment pip"""
    if sys.platform == "win32":
        return str(Path(".venv") / "Scripts" / "pip.exe")
    else:
        return str(Path(".venv") / "bin" / "pip")

def get_venv_streamlit():
    """Get the path to the virtual environment streamlit"""
    if sys.platform == "win32":
        return str(Path(".venv") / "Scripts" / "streamlit.exe")
    else:
        return str(Path(".venv") / "bin" / "streamlit")

def setup_environment():
    """Set up virtual environment and install dependencies"""
    project_dir = Path(__file__).parent
    venv_dir = project_dir / ".venv"
    requirements_file = project_dir / "requirements.txt"
    env_file = project_dir / ".env"
    env_example = project_dir / ".env.example"
    
    print(f"\n{Colors.BLUE}📁 Project directory: {project_dir}{Colors.END}\n")
    
    # Step 1: Create virtual environment
    if not venv_dir.exists():
        print(f"{Colors.YELLOW}📦 Creating virtual environment...{Colors.END}")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=project_dir)
        print(f"{Colors.GREEN}✅ Virtual environment created{Colors.END}")
    else:
        print(f"{Colors.GREEN}✅ Virtual environment exists{Colors.END}")
    
    # Step 2: Upgrade pip
    venv_pip = get_venv_pip()
    if not Path(venv_pip).exists():
        print(f"{Colors.RED}❌ Virtual environment not properly created. Please delete .venv folder and try again.{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.YELLOW}📦 Upgrading pip...{Colors.END}")
    subprocess.run([venv_pip, "install", "--upgrade", "pip", "-q"], cwd=project_dir)
    
    # Step 3: Install dependencies
    if requirements_file.exists():
        print(f"{Colors.YELLOW}📦 Installing dependencies (this may take a few minutes)...{Colors.END}")
        result = subprocess.run(
            [venv_pip, "install", "-r", "requirements.txt", "-q"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Dependencies installed{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Some dependencies may have issues, continuing...{Colors.END}")
    else:
        print(f"{Colors.RED}❌ requirements.txt not found!{Colors.END}")
        sys.exit(1)
    
    # Step 4: Set up .env file
    if not env_file.exists():
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print(f"{Colors.YELLOW}⚠️ Created .env from .env.example")
            print(f"   Please edit .env and add your GOOGLE_API_KEY{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ No .env file found. Creating default...{Colors.END}")
            with open(env_file, "w") as f:
                f.write("GOOGLE_API_KEY=your_api_key_here\n")
                f.write("LLM_PROVIDER=gemini\n")
            print(f"{Colors.YELLOW}   Please edit .env and add your GOOGLE_API_KEY{Colors.END}")
    else:
        print(f"{Colors.GREEN}✅ .env file exists{Colors.END}")
    
    # Step 5: Create data directory
    data_dir = project_dir / "data"
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
        print(f"{Colors.GREEN}✅ Created data directory{Colors.END}")
    
    return True

def kill_port(port):
    """Kill any process using the specified port"""
    try:
        if sys.platform == "win32":
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
        else:
            subprocess.run(f'lsof -ti:{port} | xargs kill -9 2>/dev/null', shell=True)
    except:
        pass

def run_application():
    """Run the Streamlit application"""
    project_dir = Path(__file__).parent
    venv_python = get_venv_python()
    venv_streamlit = get_venv_streamlit()
    
    # Kill any existing processes
    print(f"\n{Colors.YELLOW}🧹 Cleaning up old processes...{Colors.END}")
    kill_port(8501)
    kill_port(8000)
    time.sleep(1)
    
    # Suppress warnings
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    print(f"""
{Colors.GREEN}════════════════════════════════════════════════════════════════
✅ Setup Complete! Starting ORION...

📱 Frontend: http://localhost:8501
🔌 Backend:  http://localhost:8000

Press Ctrl+C to stop.
════════════════════════════════════════════════════════════════{Colors.END}
""")
    
    try:
        # Run Streamlit
        subprocess.run([
            venv_python, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ], cwd=project_dir)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Shutting down...{Colors.END}")
        time.sleep(1)
        print(f"{Colors.GREEN}✅ ORION stopped.{Colors.END}")

def main():
    print_banner()
    
    print(f"{Colors.BOLD}🚀 Starting ORION Setup & Launch...{Colors.END}\n")
    
    # Setup environment
    if not setup_environment():
        print(f"{Colors.RED}❌ Setup failed. Please check errors above.{Colors.END}")
        sys.exit(1)
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()
