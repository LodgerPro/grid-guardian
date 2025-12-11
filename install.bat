@echo off
echo ====================================================================
echo           GRID GUARDIAN - Installation Script
echo ====================================================================
echo.
echo This script will:
echo   1. Create virtual environment
echo   2. Install all dependencies
echo.
echo After installation, run: start.bat
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if venv already exists
if exist "venv\" (
    echo Virtual environment already exists. Deleting old one...
    rmdir /s /q venv
)

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo [3/3] Installing dependencies...
echo This may take 5-10 minutes depending on your internet connection...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip --quiet

REM Install in stages to show progress
echo Installing core packages (pandas, numpy)...
python -m pip install pandas>=2.0.0 numpy>=1.24.0 --quiet
if errorlevel 1 goto :install_error

echo Installing machine learning libraries (xgboost, tensorflow)...
python -m pip install xgboost>=2.0.0 scikit-learn>=1.3.0 --quiet
if errorlevel 1 goto :install_error

echo Installing visualization packages (plotly, streamlit)...
python -m pip install streamlit>=1.30.0 plotly>=5.18.0 --quiet
if errorlevel 1 goto :install_error

echo Installing data processing packages (pyarrow, tqdm)...
python -m pip install pyarrow>=14.0.0 fastparquet>=2023.10.0 tqdm>=4.66.0 --quiet
if errorlevel 1 goto :install_error

echo Installing remaining dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 goto :install_error

echo.
echo ====================================================================
echo ✓ INSTALLATION COMPLETE!
echo ====================================================================
echo.
echo Next steps:
echo   1. Test the installation:    test_generator.bat
echo   2. Generate small dataset:   python test_generator.py
echo   3. Generate full dataset:    python data/generate_data.py
echo   4. Run complete pipeline:    start.bat
echo.
echo ====================================================================
pause
exit /b 0

:install_error
echo.
echo ERROR: Failed to install dependencies
echo.
echo Try running manually:
echo   venv\Scripts\activate
echo   pip install -r requirements.txt
echo.
pause
exit /b 1
