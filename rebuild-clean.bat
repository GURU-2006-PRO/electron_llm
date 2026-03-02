@echo off
echo ========================================
echo Clean Rebuild - InsightX Analytics
echo ========================================
echo.

echo [1/5] Stopping any running processes...
taskkill /f /im "InsightX Analytics.exe" >nul 2>&1
taskkill /f /im api_server.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo.

echo [2/5] Cleaning ALL build artifacts...
if exist "release" (
    echo Removing release folder...
    rmdir /s /q release
)
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q dist
)
if exist "backend\build" (
    echo Removing backend build folder...
    rmdir /s /q backend\build
)
if exist "backend\dist" (
    echo Removing backend dist folder...
    rmdir /s /q backend\dist
)
echo Clean complete
echo.

echo [3/5] Building backend executable...
cd backend
pyinstaller build_backend.spec --clean --noconfirm
if not exist "dist\api_server.exe" (
    echo ERROR: Backend build failed!
    cd ..
    pause
    exit /b 1
)
echo Backend built: %CD%\dist\api_server.exe
cd ..
echo.

echo [4/5] Building Electron app...
call npm run build
if not exist "release\win-unpacked\InsightX Analytics.exe" (
    echo ERROR: Electron build failed!
    pause
    exit /b 1
)
echo Electron app built
echo.

echo [5/5] Copying backend files to release...
echo Creating backend folders...
if not exist "release\win-unpacked\resources\backend\dist" mkdir release\win-unpacked\resources\backend\dist
if not exist "release\win-unpacked\resources\backend\data" mkdir release\win-unpacked\resources\backend\data

echo Copying backend exe...
copy /Y backend\dist\api_server.exe release\win-unpacked\resources\backend\dist\

echo Copying data files...
copy /Y backend\data\*.* release\win-unpacked\resources\backend\data\

echo Copying .env...
copy /Y backend\.env release\win-unpacked\resources\backend\

echo Verifying...
if exist "release\win-unpacked\resources\backend\dist\api_server.exe" (
    echo [OK] Backend exe copied
) else (
    echo [FAIL] Backend exe missing!
)

if exist "release\win-unpacked\resources\backend\data\upi_transactions_2024.csv" (
    echo [OK] Data file copied
) else (
    echo [FAIL] Data file missing!
)

if exist "release\win-unpacked\resources\backend\.env" (
    echo [OK] .env copied
) else (
    echo [FAIL] .env missing!
)
echo.

echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Your EXE is at: release\win-unpacked\InsightX Analytics.exe
echo.
echo To test:
echo   cd release\win-unpacked
echo   "InsightX Analytics.exe"
echo.
echo The backend should start automatically now.
echo Press Ctrl+Shift+I to see [BACKEND] messages in console.
echo.
pause
