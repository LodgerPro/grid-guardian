# Grid Guardian - Project Structure

```
grid-guardian/
│
├── app/                                    # Streamlit Dashboard Application
│   ├── Home.py                            # Main dashboard homepage
│   └── pages/                             # Dashboard pages
│       ├── 1_📊_Monitoring.py             # Real-time monitoring page
│       ├── 2_🔮_Predictions.py            # AI predictions page
│       ├── 3_💰_Financial.py              # Financial analysis page
│       └── 4_🗺️_Maps.py                   # Geographic map page
│
├── config/                                 # Configuration Management
│   ├── __init__.py                        # Config module initialization
│   └── settings.py                        # Centralized settings and parameters
│
├── data/                                   # Data Directory
│   ├── generate_data.py                   # Data generation script
│   ├── raw/                               # Raw data (generated)
│   │   ├── grid_sensor_data.csv           # Sensor readings
│   │   └── equipment_locations.csv        # Equipment GPS data
│   └── processed/                         # Processed data (generated)
│       ├── cleaned_data.csv               # Cleaned sensor data
│       └── features.csv                   # Engineered features
│
├── models/                                 # Machine Learning Models
│   ├── __init__.py                        # Models module initialization
│   ├── train_xgboost.py                   # XGBoost training script
│   ├── train_lstm.py                      # LSTM training script
│   └── saved/                             # Trained models (generated)
│       ├── xgboost_model_latest.pkl       # Latest XGBoost model
│       ├── xgboost_metadata_latest.json   # XGBoost metadata
│       ├── lstm_model_latest.h5           # Latest LSTM model
│       ├── lstm_scaler_latest.pkl         # LSTM scaler
│       └── lstm_metadata_latest.json      # LSTM metadata
│
├── src/                                    # Source Code
│   ├── __init__.py                        # Source module initialization
│   ├── preprocessing.py                   # Data cleaning and validation
│   └── feature_engineering.py             # Feature creation pipeline
│
├── logs/                                   # Application Logs (generated)
│   └── grid_guardian.log                  # Application log file
│
├── .gitignore                             # Git ignore rules
├── README.md                              # Project documentation
├── requirements.txt                       # Python dependencies
├── run_pipeline.py                        # Complete pipeline runner
├── quickstart.bat                         # Windows quick start script
├── quickstart.sh                          # Linux/Mac quick start script
└── PROJECT_STRUCTURE.md                   # This file
```

## Directory Descriptions

### `/app` - Dashboard Application
Interactive Streamlit web application for visualization and monitoring.
- **Home.py**: Main entry point with overview dashboard
- **pages/**: Multi-page dashboard components
  - Monitoring: Real-time sensor visualization
  - Predictions: AI-powered failure predictions
  - Financial: ROI and cost analysis
  - Maps: Geographic equipment visualization

### `/config` - Configuration
Centralized configuration management for the entire project.
- Settings for data paths, model parameters, thresholds, and more
- Easy customization without modifying code

### `/data` - Data Storage
Contains all data files and generation scripts.
- **generate_data.py**: Creates synthetic grid sensor data
- **raw/**: Original unprocessed data
- **processed/**: Cleaned and feature-engineered data

### `/models` - Machine Learning
Model training scripts and saved model artifacts.
- **train_xgboost.py**: Gradient boosting model training
- **train_lstm.py**: Deep learning LSTM model training
- **saved/**: Trained model files with timestamps

### `/src` - Source Code
Core data processing modules.
- **preprocessing.py**: Data cleaning, outlier handling, validation
- **feature_engineering.py**: Advanced feature creation (100+ features)

### `/logs` - Logging
Application logs for debugging and monitoring.

## Key Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `run_pipeline.py` | End-to-end pipeline execution |
| `quickstart.bat/sh` | One-click setup and launch |
| `.gitignore` | Git version control exclusions |
| `README.md` | Comprehensive project documentation |

## Generated Directories

These directories are created automatically when running the pipeline:

- `data/raw/` - Created by data generation
- `data/processed/` - Created by preprocessing
- `models/saved/` - Created by model training
- `logs/` - Created by application logging

## File Counts

- **Python Scripts**: 11 core files
- **Dashboard Pages**: 5 (Home + 4 pages)
- **Configuration**: 2 files
- **Documentation**: 3 files (README, PROJECT_STRUCTURE, .gitignore)
- **Scripts**: 2 (quickstart.bat, quickstart.sh)

## Workflow

1. **Setup**: Run `quickstart.bat` (Windows) or `quickstart.sh` (Linux/Mac)
2. **Data Generation**: `python data/generate_data.py`
3. **Preprocessing**: `python src/preprocessing.py`
4. **Feature Engineering**: `python src/feature_engineering.py`
5. **Model Training**: `python models/train_xgboost.py` and `python models/train_lstm.py`
6. **Dashboard**: `streamlit run app/Home.py`

Or simply: `python run_pipeline.py` to run all steps automatically!

## Technology Stack

- **Language**: Python 3.9+
- **ML**: XGBoost, TensorFlow, scikit-learn
- **Dashboard**: Streamlit
- **Visualization**: Plotly, Folium
- **Data**: Pandas, NumPy

## Production Readiness

✓ Modular architecture
✓ Configuration management
✓ Error handling and logging
✓ Documentation
✓ Version control ready
✓ Automated pipeline
✓ Multiple deployment options

---

Last Updated: 2025
