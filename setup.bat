@echo off
:: ==============================================================================
:: City Bus Management System for Amravati
:: One-Time Setup Script - Run this FIRST before starting the app
:: ==============================================================================
title Amravati Bus System - Setup

echo.
echo ============================================================
echo   AMRAVATI CITY BUS MANAGEMENT SYSTEM - SETUP
echo ============================================================
echo.

:: Step 1: Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python is NOT installed or not in PATH.
    echo         Download Python 3.9+ from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo [OK] Python found.

:: Step 2: Check pip
pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] pip is not available. Please reinstall Python.
    pause
    exit /b 1
)
echo [OK] pip found.

:: Step 3: Create virtual environment
cd /d "%~dp0backend"
IF NOT EXIST "venv" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) ELSE (
    echo [OK] Virtual environment already exists.
)

:: Step 4: Install requirements
call venv\Scripts\activate.bat
echo [SETUP] Installing Python packages...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to install packages.
    pause
    exit /b 1
)
echo [OK] All packages installed.

echo.
echo ============================================================
echo   NEXT STEP: Configure MySQL Database
echo ============================================================
echo.
echo 1. Open MySQL Workbench or MySQL Command Line Client
echo 2. Run this file: database\schema.sql
echo 3. Run this file: database\sample_data.sql
echo.
echo After that, update backend\.env with your MySQL password:
echo   DB_PASSWORD=your_mysql_root_password
echo.
echo Then double-click start.bat to launch the application!
echo.
echo ============================================================

pause
