@echo off
title Consultant Bench Management System - Local Deployment

echo ============================================
echo   Consultant Bench Management System
echo   Local Deployment Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✓ Python and Node.js are available
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment and install backend dependencies
echo.
echo Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some backend dependencies may have failed to install
    echo This is normal for ML packages - the system will work without them
)
echo ✓ Backend dependencies installed

REM Install frontend dependencies
echo.
echo Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    npm install >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        echo Please run 'npm install' manually in the frontend directory
        pause
        exit /b 1
    )
    echo ✓ Frontend dependencies installed
) else (
    echo ✓ Frontend dependencies already installed
)
cd ..

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: No .env file found
    echo Creating default .env file...
    echo DATABASE_URL=postgresql://consultant_user:password@localhost:5432/consultant_bench_db > .env
    echo SECRET_KEY=dev-secret-key-change-in-production >> .env
    echo DEBUG=True >> .env
    echo CORS_ORIGINS=http://localhost:3000,http://localhost:5173 >> .env
    echo UPLOAD_DIR=./uploads >> .env
    echo MAX_FILE_SIZE=10485760 >> .env
    echo ✓ Default .env file created
    echo.
    echo IMPORTANT: Please update the database credentials in .env file
    echo           and ensure PostgreSQL is running with the correct database
)

echo.
echo ============================================
echo   Starting Services
echo ============================================
echo.

echo Starting backend server...
start "Backend Server" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && python simple_backend.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting frontend development server...
start "Frontend Server" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ============================================
echo   Deployment Complete!
echo ============================================
echo.
echo Services are starting in separate windows:
echo.
echo 🚀 Backend API:      http://localhost:8000
echo 📝 API Docs:         http://localhost:8000/docs
echo 🌐 Frontend App:     http://localhost:3000
echo 👤 Profile Page:     http://localhost:3000/profile
echo.
echo Note: Frontend may take a few moments to compile and start
echo      Check the frontend window for the actual port if 3000 is busy
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open the application in default browser
start http://localhost:3000

echo.
echo To stop the services, close the Backend Server and Frontend Server windows
echo or press Ctrl+C in each window
echo.
pause
