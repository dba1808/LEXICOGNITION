@echo off
echo 🛑 Stopping LexiCognition services...
echo.

REM Kill processes on port 8000 (Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing Backend process (PID %%a)...
    taskkill /PID %%a /F
)

REM Kill processes on port 8501 (Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    echo Killing Frontend process (PID %%a)...
    taskkill /PID %%a /F
)

echo.
echo ✅ All services stopped!
pause
