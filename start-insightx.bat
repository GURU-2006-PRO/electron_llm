@echo off
echo ========================================
echo Starting InsightX Analytics
echo ========================================
echo.

echo Starting Python Backend...
start "InsightX Backend" cmd /k "cd backend && python app_simple.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting InsightX App...
call npm start

echo.
echo ========================================
echo InsightX is running!
echo ========================================
