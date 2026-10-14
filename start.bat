@echo off
:: ==============================================================================
:: City Bus Management System for Amravati
:: Windows Startup Script
:: ==============================================================================
title Amravati City Bus Management System

echo.
echo ============================================================
echo   AMRAVATI CITY BUS MANAGEMENT SYSTEM
echo   Starting Backend Server...
echo ============================================================
echo.

:: Navigate to backend folder
cd /d "%~dp0backend"

:: Check if virtual environment exists
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [SETUP] Virtual environment not found. Creating one...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to create virtual environment.
        echo         Make sure Python 3.9+ is installed and in PATH.
        pause
        exit /b 1
    )
    echo [SETUP] Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

echo.
echo [INFO] Virtual environment activated.
echo [INFO] Starting Flask server on http://127.0.0.1:5000
echo [INFO] Press CTRL+C to stop the server.
echo.
echo ============================================================
echo   Open your browser and go to: http://127.0.0.1:5000
echo   Admin Login : username = admin    password = Admin@123
echo   Passenger   : username = rahul_sharma  password = Passenger@123
echo ============================================================
echo.

python app.py

pause
