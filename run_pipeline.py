"""
Complete End-to-End Pipeline Runner
Executes the full data processing and model training workflow

NOTE: This pipeline uses a REDUCED dataset by default for faster execution:
  - 50 substations (instead of 500)
  - 3 months of data (instead of 2 years)
  - ~1,080,000 rows (instead of 87,600,000)

To generate the FULL dataset (87.6M rows), edit the configuration in
run_data_generation() or run data/generate_data.py directly.
"""

import os
import sys
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def run_data_generation():
    """Step 1: Generate synthetic data"""
    print_header("STEP 1: Data Generation")
    from data.generate_data import GridDataGenerator, generate_location_data

    # Configuration - using smaller dataset for faster pipeline
    # For full dataset (87.6M rows), use: n_substations=500, hours=17520
    N_SUBSTATIONS = 50           # Reduced from 500 for faster testing
    EQUIPMENT_PER_SUBSTATION = 10
    HOURS = 2160                 # 3 months instead of 2 years

    print(f"\nPipeline configuration:")
    print(f"  Substations: {N_SUBSTATIONS}")
    print(f"  Equipment per substation: {EQUIPMENT_PER_SUBSTATION}")
    print(f"  Total equipment: {N_SUBSTATIONS * EQUIPMENT_PER_SUBSTATION}")
    print(f"  Hours: {HOURS} ({HOURS/8760:.1f} years)")
    print(f"  Total rows: {N_SUBSTATIONS * EQUIPMENT_PER_SUBSTATION * HOURS:,}")

    # Generate telemetry data
    generator = GridDataGenerator(
        n_substations=N_SUBSTATIONS,
        equipment_per_substation=EQUIPMENT_PER_SUBSTATION,
        hours=HOURS
    )
    telemetry_file = generator.generate_and_save_parquet('data/raw')

    # Generate location data
    generate_location_data(N_SUBSTATIONS, EQUIPMENT_PER_SUBSTATION)

    print("[OK] Data generation completed successfully!")


def run_preprocessing():
    """Step 2: Preprocess raw data"""
    print_header("STEP 2: Data Preprocessing")

    print("[WARNING]  Note: Preprocessing expects CSV format")
    print("Converting Parquet to CSV for compatibility...")

    import pandas as pd

    # Convert Parquet to CSV for preprocessing
    df = pd.read_parquet('data/raw/grid_telemetry_data.parquet')
    df.to_csv('data/raw/grid_sensor_data.csv', index=False)
    print(f"[OK] Converted {len(df):,} rows to CSV")

    from src.preprocessing import preprocess_pipeline

    preprocess_pipeline(
        input_path='data/raw/grid_sensor_data.csv',
        output_path='data/processed/cleaned_data.csv',
        balance_method='none'
    )

    print("[OK] Preprocessing completed successfully!")


def run_feature_engineering():
    """Step 3: Engineer features"""
    print_header("STEP 3: Feature Engineering")
    from src.feature_engineering import feature_engineering_pipeline

    feature_engineering_pipeline(
        input_path='data/processed/cleaned_data.csv',
        output_path='data/processed/features.csv'
    )

    print("[OK] Feature engineering completed successfully!")


def run_xgboost_training():
    """Step 4: Train XGBoost model"""
    print_header("STEP 4: XGBoost Model Training")
    from models.train_xgboost import main as train_xgboost

    train_xgboost()

    print("[OK] XGBoost training completed successfully!")


def run_lstm_training():
    """Step 5: Train LSTM model (optional, memory-intensive)"""
    print_header("STEP 5: LSTM Model Training (Optional)")
    print("[WARNING]  Note: LSTM training requires significant memory (8+ GB RAM)")
    print("   XGBoost model is already trained and sufficient for most use cases.")
    print("   You can skip LSTM training and use XGBoost only.\n")

    try:
        from models.train_lstm import main as train_lstm
        train_lstm()
        print("[OK] LSTM training completed successfully!")
    except MemoryError as e:
        print(f"\n[WARNING]  LSTM training skipped due to insufficient memory")
        print(f"   Error: {e}")
        print("   This is OK - XGBoost model is already trained and working!")
        print("[OK] Continuing without LSTM model...")
    except Exception as e:
        print(f"\n[WARNING]  LSTM training failed: {e}")
        print("   This is OK - XGBoost model is already trained and working!")
        print("[OK] Continuing without LSTM model...")


def main():
    """Run complete pipeline"""
    start_time = datetime.now()

    print("\n")
    print("=" * 70)
    print("    GRID GUARDIAN - COMPLETE PIPELINE")
    print("=" * 70)
    print(f"\nStarted at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Initialize directories
        print_header("Initializing Project Structure")
        from config.settings import initialize_directories
        initialize_directories()
        print("[OK] Directories initialized")

        # Run pipeline steps
        steps = [
            ("Data Generation", run_data_generation),
            ("Data Preprocessing", run_preprocessing),
            ("Feature Engineering", run_feature_engineering),
            ("XGBoost Training", run_xgboost_training),
            ("LSTM Training", run_lstm_training)
        ]

        for step_name, step_func in steps:
            try:
                step_func()
            except Exception as e:
                print(f"\n[ERROR] Error in {step_name}: {str(e)}")
                print("Pipeline execution stopped.")
                sys.exit(1)

        # Summary
        end_time = datetime.now()
        duration = end_time - start_time

        print_header("PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"\nStart Time:    {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time:      {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration:      {duration}")

        print("\n" + "=" * 70)
        print("Next Steps:")
        print("  1. Review model performance metrics in models/saved/")
        print("  2. Launch the dashboard: streamlit run app/Home.py")
        print("  3. Explore predictions and monitoring features")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n[WARNING]  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
