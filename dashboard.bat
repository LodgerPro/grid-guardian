@echo off
echo ====================================================================
echo           GRID GUARDIAN - Dashboard
echo ====================================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ====================================================================
echo Starting Streamlit dashboard...
echo Dashboard will open at http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo ====================================================================
echo.

streamlit run app/Home.py

pause
