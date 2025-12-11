@echo off
echo ====================================================================
echo           GRID GUARDIAN - Quick Start Script
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies (this may take 5-10 minutes)...
echo Installing core packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully

echo [4/5] Running complete pipeline...
python run_pipeline.py
if errorlevel 1 (
    echo ERROR: Pipeline execution failed
    pause
    exit /b 1
)

echo [5/5] Launching dashboard...
echo.
echo ====================================================================
echo Dashboard will open at http://localhost:8501
echo Press Ctrl+C to stop the dashboard
echo ====================================================================
echo.
streamlit run app/Home.py

pause
