# Grid Guardian - Project Structure Analysis

## Executive Summary
Grid Guardian is a predictive maintenance system for electrical grid equipment with:
- **876,000 telemetry records** (2 years of data)
- **50 equipment units** (10 substations × 5 units each)
- **3-level risk classification** (Low: 74.9%, Medium: 20.1%, High: 5.0%)
- **Russian-language Streamlit interface**

## Directory Structure
```
grid-guardian/
├── app/
│   ├── Home.py                          # Main dashboard page
│   └── pages/
│       ├── 1_📊_Monitoring.py          # Real-time monitoring
│       ├── 2_🔮_Predictions.py         # ML predictions
│       ├── 3_💰_Financial.py           # Cost analysis
│       └── 4_🗺️_Maps.py                # Geographic visualization
├── data/
│   ├── generate_data.py                 # Data generator (main)
│   ├── generate_data_full.py           # Full dataset generator
│   ├── raw/
│   │   ├── grid_telemetry_data.parquet # 876K records, 18 columns
│   │   └── equipment_locations.parquet  # 50 equipment locations
│   ├── processed/
│   │   ├── cleaned_data.csv             # Preprocessed data
│   │   └── features.csv                 # 95 engineered features
│   └── test/
│       └── grid_telemetry_data.parquet  # Test dataset
├── src/
│   ├── preprocessing.py                 # Data cleaning pipeline
│   └── feature_engineering.py           # Feature creation + risk labels
├── models/
│   ├── train_xgboost.py                # XGBoost classifier
│   ├── train_lstm.py                    # LSTM model (TensorFlow)
│   └── saved/                           # Trained models
├── config/
│   └── settings.py                      # Configuration
└── tests/                               # ← NEW: Test suite
```

## Data Files

### Raw Telemetry Data
- **Path**: `data/raw/grid_telemetry_data.parquet`
- **Shape**: (876,000, 18)
- **Size**: ~76 MB
- **Period**: 2 years (2023-01-01 to 2024-12-30)
- **Equipment**: 50 units (SUB001_EQ01 to SUB010_EQ05)

**Columns (18)**:
```python
[
    'timestamp',           # datetime64[ns]
    'equipment_id',        # object
    'temperature_top',     # float32
    'temperature_oil',     # float32
    'voltage_phase_a',     # float32
    'voltage_phase_b',     # float32
    'voltage_phase_c',     # float32
    'current_phase_a',     # float32
    'current_phase_b',     # float32
    'current_phase_c',     # float32
    'gas_h2',              # float32 (DGA)
    'gas_ch4',             # float32 (DGA)
    'gas_c2h2',            # float32 (DGA)
    'vibration_x',         # float32
    'vibration_y',         # float32
    'vibration_z',         # float32
    'humidity',            # float32
    'load_percentage'      # float32
]
```

### Equipment Locations
- **Path**: `data/raw/equipment_locations.parquet`
- **Shape**: (50, 14)
- **Equipment**: 10 substations × 5 units
- **Coverage**: 5 Russian Federal Districts

### Processed Features
- **Path**: `data/processed/features.csv`
- **Shape**: (876,000, 95)
- **Features**: 18 raw + 77 engineered
- **Risk levels**: 0 (low), 1 (medium), 2 (high)

**Feature Categories**:
- Temporal (8): hour, day_of_week, month, is_weekend, hour_sin, hour_cos, day_sin, day_cos
- Rolling statistics (16): 3h, 6h, 12h, 24h windows (mean, std, min, max)
- Equipment dummies (50): One-hot encoded equipment_id
- Risk labels (3): failure, risk_level, failure_probability

## Application Structure

### Home.py
**Purpose**: Main dashboard with KPIs and risk overview

**Key Functions**:
- `load_sample_data()`: Load & cache features.csv with stratified sampling
- `display_key_metrics()`: Show equipment count, high risk count, avg temp
- `display_risk_overview()`: Risk distribution chart (uses risk_level)
- `display_equipment_status()`: Equipment table with status icons

**Caching**: `@st.cache_data(ttl=300)` - 5 minute TTL

**Data Flow**:
```
features.csv → load_sample_data() → stratified sample (50K records)
→ proportional risk distribution (75%/20%/5%)
→ dashboard metrics & visualizations
```

### Pages

#### 1. Monitoring (1_📊_Monitoring.py)
- Real-time telemetry visualization
- Sensor readings over time
- Equipment health indicators

#### 2. Predictions (2_🔮_Predictions.py)
**Purpose**: ML-based failure prediction

**Key Functions**:
- `load_prediction_data()`: Load features with proportional sampling (10K records)
- `load_model()`: Load XGBoost model from pickle
- Risk factor analysis (temperature, vibration, age)
- Critical equipment recommendations

**Critical Logic**:
- Uses `risk_level` for classification (not failure_probability thresholds)
- Counts UNIQUE equipment (not records)
- Shows worst-case metrics per equipment

#### 3. Financial (3_💰_Financial.py)
- Cost-benefit analysis
- Maintenance cost tracking
- ROI calculations

#### 4. Maps (4_🗺️_Maps.py)
**Purpose**: Geographic visualization

**Key Functions**:
- `load_location_data()`: Load equipment_locations.parquet + merge with risk data
- Dynamic zoom level based on geographic spread
- Risk-colored markers on Folium map

**Substations** (10):
- Central FD: Podolsk, Tula
- Southern FD: Krasnodar, Rostov-on-Don
- Volga FD: Kazan, Nizhny Novgorod
- Siberian FD: Novosibirsk, Krasnoyarsk
- Northwestern FD: St. Petersburg, Murmansk

## Key Functions Identified

### Risk Calculation
**File**: `src/feature_engineering.py`

**Function**: `create_failure_labels()`
```python
def create_failure_labels(self):
    """
    Create 3-level risk classification:
    - risk_level = 0 (Low): Normal operation
    - risk_level = 1 (Medium): Warning conditions
    - risk_level = 2 (High): Critical, likely failure

    Logic:
    - High risk: temp > 100°C OR gas_c2h2 > 100ppm OR vibration > 8mm/s
    - Medium risk: temp > 85°C OR gas_c2h2 > 50ppm OR vibration > 5mm/s
    - Low risk: Everything else
    """
```

**Distribution**:
- Low: 656,178 records (74.9%)
- Medium: 176,022 records (20.1%)
- High: 43,800 records (5.0%)

### Data Aggregation
**Pattern**: Equipment-level aggregation for dashboards
```python
equipment_summary = df.groupby('equipment_id').agg({
    'temperature': 'mean',
    'vibration': 'mean',
    'risk_level': 'max',  # Worst case
    'failure_probability': 'max'
}).reset_index()
```

### Stratified Sampling
**Purpose**: Maintain risk distribution in samples
```python
# Proportional sampling (Home.py)
for level in [0, 1, 2]:
    proportion = risk_counts[level] / len(df)
    sample_size = int(total_sample * proportion)
    # Sample ~37.5K/10K/2.5K for 50K total
```

## Dependencies

**Core** (requirements.txt):
```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
tensorflow>=2.15.0
streamlit>=1.30.0
plotly>=5.18.0
folium>=0.15.0
pyarrow>=14.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Configuration

**Data Generation** (test_generator.py):
```python
N_SUBSTATIONS = 10
EQUIPMENT_PER_SUBSTATION = 5
HOURS = 17520  # 2 years
```

**Total Records**: 10 × 5 × 17,520 = 876,000

**Risk Distribution**:
- Target: 5% high, 20% medium, 75% low
- Actual: Matches target within 0.1%

## Testing Requirements

Based on this analysis, tests must verify:

1. **Data Integrity**
   - 876,000 records in telemetry
   - 50 equipment units
   - 18 raw columns present
   - No nulls in critical columns
   - Realistic value ranges

2. **Risk Classification**
   - 3 levels (0, 1, 2)
   - Correct distribution (75%/20%/5%)
   - Unique equipment count vs. record count

3. **Sampling**
   - Stratified sampling preserves proportions
   - No duplicate equipment in unique lists

4. **Russian Language**
   - All UI text in Russian
   - Proper Cyrillic encoding

5. **Performance**
   - Data loads < 5s
   - Aggregations < 2s
   - Page renders without errors

6. **Integration**
   - Data → Preprocessing → Features → ML → Dashboard
   - All pages load successfully
   - Caching works correctly
