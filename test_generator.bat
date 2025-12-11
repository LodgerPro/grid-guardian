@echo off
echo ====================================================================
echo           GRID GUARDIAN - Test Data Generator
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
echo Testing data generator with small dataset...
echo This will generate ~8,400 rows (50 equipment × 168 hours)
echo ====================================================================
echo.

python test_generator.py

if errorlevel 1 (
    echo.
    echo ERROR: Test failed
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo ✓ Test completed successfully!
echo ====================================================================
echo.
echo To generate full dataset (87.6M rows):
echo   python data/generate_data.py
echo.
pause
