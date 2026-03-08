@echo off
echo ========================================
echo Building InsightX for Distribution
echo ========================================
echo.

REM Step 1: Backup your current .env with keys
echo [1/4] Backing up your API keys...
copy backend\.env backend\.env.mykeys >nul 2>&1
echo Done!
echo.

REM Step 2: Clear .env for distribution
echo [2/4] Clearing API keys for distribution...
(
echo # ===== API KEYS - KEEP SECRET =====
echo # Get your API keys from:
echo # - OpenRouter: https://openrouter.ai/keys
echo # - Gemini: https://aistudio.google.com/app/apikey
echo # - Groq: https://console.groq.com/keys
echo.
echo # OpenRouter (DeepSeek models^) - Optional fallback
echo OPENROUTER_API_KEY=
echo.
echo # Google Gemini API Keys (3 keys for different models^)
echo # Gemini 3.0 Flash Preview (Primary - 20 req/day^)
echo GEMINI_API_KEY_3_FLASH=
echo.
echo # Gemini 2.5 Flash (Fallback 1 - 1500 req/day^)
echo GEMINI_API_KEY_2_5_FLASH_1=
echo.
echo # Gemini 2.5 Flash (Fallback 2 - 1500 req/day^)
echo GEMINI_API_KEY_2_5_FLASH_2=
echo.
echo # Groq (Fast inference - 500K free tokens/day^)
echo GROQ_API_KEY=
echo.
echo # ===== DATABASE SETTINGS =====
echo DATABASE_PATH=data/chat_history.db
echo.
echo # ===== SERVER SETTINGS =====
echo FLASK_DEBUG=True
echo FLASK_PORT=5000
echo FLASK_HOST=127.0.0.1
) > backend\.env
echo Done!
echo.

REM Step 3: Build the EXE
echo [3/4] Building EXE...
call npm run build
echo.

REM Step 4: Restore your keys
echo [4/4] Restoring your API keys...
copy backend\.env.mykeys backend\.env >nul 2>&1
echo Done!
echo.

echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo EXE Location: release\InsightX Analytics Setup 1.0.0.exe
echo Your API keys: RESTORED in backend\.env
echo.
echo You can now:
echo 1. Use the app normally (your keys are back)
echo 2. Share the EXE with friends (no keys included)
echo.
pause
