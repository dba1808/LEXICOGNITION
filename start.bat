@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           🎓 LexiCognition - Starting...                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Kill any existing processes on ports 8000 and 8501
echo 🧹 Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do taskkill /PID %%a /F 2>nul
timeout /t 2 /nobreak >nul

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found. Using system Python.
)

REM Suppress TensorFlow warnings
set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2

echo.
echo 🚀 Starting Backend (FastAPI) on port 8000...
start "LexiCognition-Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo ⏳ Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo 🌐 Starting Frontend (Streamlit) on port 8501...
start "LexiCognition-Frontend" cmd /k "python -m streamlit run frontend/app.py --server.port 8501"

echo.
echo ✅ Services starting in separate windows!
echo.
echo 📱 Frontend: http://localhost:8501
echo 🔌 Backend API: http://localhost:8000
echo.
echo Press Ctrl+C in each window to stop the services.
echo.
pause
