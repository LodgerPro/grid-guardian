@echo off
echo ====================================================================
echo           GRID GUARDIAN - Full Pipeline Execution
echo ====================================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

echo Step 1: Copying test data to raw directory...
cp data/test/grid_telemetry_data.parquet data/raw/grid_telemetry_data.parquet
echo.

echo Step 2: Converting Parquet to CSV...
venv\Scripts\python.exe -c "import pandas as pd; df = pd.read_parquet('data/raw/grid_telemetry_data.parquet'); df.to_csv('data/raw/grid_sensor_data.csv', index=False); print(f'Converted {len(df):,} rows')"
echo.

echo Step 3: Running preprocessing...
venv\Scripts\python.exe -c "from src.preprocessing import preprocess_pipeline; preprocess_pipeline('data/raw/grid_sensor_data.csv', 'data/processed/cleaned_data.csv', balance_method='none')"
echo.

echo Step 4: Running feature engineering...
venv\Scripts\python.exe -c "from src.feature_engineering import feature_engineering_pipeline; feature_engineering_pipeline('data/processed/cleaned_data.csv', 'data/processed/features.csv')"
echo.

echo Step 5: Training XGBoost model...
venv\Scripts\python.exe -c "from models.train_xgboost import main; main()"
echo.

echo ====================================================================
echo Pipeline completed successfully!
echo ====================================================================
echo.
pause
