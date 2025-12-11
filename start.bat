@echo off
echo ====================================================================
echo           GRID GUARDIAN - Start Pipeline
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
echo Starting complete pipeline...
echo ====================================================================
echo.

python run_pipeline.py

if errorlevel 1 (
    echo.
    echo ====================================================================
    echo ERROR: Pipeline execution failed
    echo ====================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo ✓ Pipeline completed successfully!
echo ====================================================================
echo.
echo To launch the dashboard:
echo   dashboard.bat
echo.
pause
