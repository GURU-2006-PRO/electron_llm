@echo off
echo ========================================
echo Restoring Your API Keys
echo ========================================
echo.

if exist backend\.env.mykeys (
    copy backend\.env.mykeys backend\.env >nul 2>&1
    echo [SUCCESS] Your API keys have been restored!
    echo.
    echo You can now use the app normally.
) else (
    echo [ERROR] Backup file not found!
    echo.
    echo Please paste your API keys manually:
    echo 1. Open backend\.env
    echo 2. Add your keys
    echo 3. Save the file
)

echo.
pause
