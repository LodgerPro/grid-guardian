"""
Configuration Settings for Grid Guardian
Centralized configuration management
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Model paths
MODEL_DIR = BASE_DIR / 'models'
SAVED_MODEL_DIR = MODEL_DIR / 'saved'

# Data files
RAW_SENSOR_DATA = RAW_DATA_DIR / 'grid_sensor_data.csv'
EQUIPMENT_LOCATIONS = RAW_DATA_DIR / 'equipment_locations.csv'
CLEANED_DATA = PROCESSED_DATA_DIR / 'cleaned_data.csv'
FEATURES_DATA = PROCESSED_DATA_DIR / 'features.csv'

# Model files
XGBOOST_MODEL = SAVED_MODEL_DIR / 'xgboost_model_latest.pkl'
LSTM_MODEL = SAVED_MODEL_DIR / 'lstm_model_latest.h5'
LSTM_SCALER = SAVED_MODEL_DIR / 'lstm_scaler_latest.pkl'

# Data generation settings
DATA_GENERATION = {
    'n_samples': 50000,
    'failure_rate': 0.08,
    'random_seed': 42
}

# Feature engineering settings
FEATURE_ENGINEERING = {
    'rolling_windows': [3, 6, 12, 24],  # hours
    'lag_features': [1, 3, 6, 12],  # hours
    'sensor_columns': [
        'temperature',
        'vibration',
        'current',
        'voltage',
        'power_factor',
        'oil_level',
        'humidity'
    ]
}

# Model training settings
XGBOOST_PARAMS = {
    'max_depth': 5,
    'learning_rate': 0.1,
    'n_estimators': 200,
    'min_child_weight': 3,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'binary:logistic',
    'random_state': 42,
    'eval_metric': 'auc'
}

LSTM_PARAMS = {
    'sequence_length': 24,
    'lstm_units': [128, 64, 32],
    'dropout_rate': [0.3, 0.3, 0.2],
    'dense_units': [16],
    'learning_rate': 0.001,
    'batch_size': 32,
    'epochs': 50
}

# Risk thresholds
RISK_THRESHOLDS = {
    'high': 0.7,
    'medium': 0.3,
    'low': 0.0
}

# Sensor thresholds
SENSOR_THRESHOLDS = {
    'temperature': {
        'warning': 85,
        'critical': 100,
        'normal': 65
    },
    'vibration': {
        'warning': 5,
        'critical': 8,
        'normal': 2.5
    },
    'voltage': {
        'min': 220,
        'max': 240,
        'normal': 230
    },
    'power_factor': {
        'warning': 0.85,
        'critical': 0.75,
        'normal': 0.95
    },
    'oil_level': {
        'warning': 60,
        'critical': 40,
        'normal': 85
    }
}

# Financial settings
FINANCIAL_PARAMS = {
    'unplanned_outage_cost': 500000,
    'planned_maintenance_cost': 50000,
    'equipment_replacement_cost': 2000000,
    'implementation_cost': 500000,
    'annual_operating_cost': 100000
}

# Dashboard settings
DASHBOARD_CONFIG = {
    'page_title': 'Grid Guardian - Predictive Maintenance',
    'page_icon': '⚡',
    'layout': 'wide',
    'refresh_interval': 60,  # seconds
    'max_display_records': 100
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': BASE_DIR / 'logs' / 'grid_guardian.log'
}

# Equipment types
EQUIPMENT_TYPES = [
    'Transformer',
    'Generator',
    'Transmission Line',
    'Substation',
    'Circuit Breaker',
    'Capacitor Bank'
]

# Alert configuration
ALERT_CONFIG = {
    'enable_email': False,
    'enable_sms': False,
    'enable_dashboard': True,
    'high_risk_immediate': True,
    'medium_risk_daily': True
}

# API settings (for future integration)
API_CONFIG = {
    'enable_api': False,
    'api_host': '0.0.0.0',
    'api_port': 8000,
    'api_version': 'v1'
}

# Create directories if they don't exist
def initialize_directories():
    """Create necessary directories"""
    directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        SAVED_MODEL_DIR,
        BASE_DIR / 'logs'
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    print("Grid Guardian Configuration")
    print("=" * 50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Model Directory: {MODEL_DIR}")
    print("\nInitializing directories...")
    initialize_directories()
    print("Configuration complete!")
