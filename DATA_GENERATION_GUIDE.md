# Data Generation Guide

## Overview

The enhanced data generator creates a realistic, large-scale power grid telemetry dataset suitable for training predictive maintenance models.

## Specifications

### Scale
- **Substations**: 500
- **Equipment per substation**: 10
- **Total equipment**: 5,000 units
- **Time period**: 2 years (17,520 hours)
- **Total rows**: **87,600,000** (87.6 million)

### Equipment Naming
```
Format: SUB{substation_id:03d}_EQ{equipment_id:02d}
Examples: SUB001_EQ01, SUB245_EQ07, SUB500_EQ10
```

## Data Schema

### Telemetry Columns (18 total)

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `timestamp` | datetime | Measurement timestamp | 2023-01-01 to 2024-12-31 |
| `equipment_id` | string | Unique equipment identifier | SUB001_EQ01 - SUB500_EQ10 |
| `temperature_top` | float32 | Top oil temperature (°C) | 20-150 |
| `temperature_oil` | float32 | Oil temperature (°C) | 20-120 |
| `voltage_phase_a` | float32 | Phase A voltage (kV) | 200-250 |
| `voltage_phase_b` | float32 | Phase B voltage (kV) | 200-250 |
| `voltage_phase_c` | float32 | Phase C voltage (kV) | 200-250 |
| `current_phase_a` | float32 | Phase A current (A) | 0-800 |
| `current_phase_b` | float32 | Phase B current (A) | 0-800 |
| `current_phase_c` | float32 | Phase C current (A) | 0-800 |
| `gas_h2` | float32 | Dissolved hydrogen (ppm) | 0-500 |
| `gas_ch4` | float32 | Dissolved methane (ppm) | 0-300 |
| `gas_c2h2` | float32 | Dissolved acetylene (ppm) | 0-200 |
| `vibration_x` | float32 | X-axis vibration (mm/s) | 0-20 |
| `vibration_y` | float32 | Y-axis vibration (mm/s) | 0-20 |
| `vibration_z` | float32 | Z-axis vibration (mm/s) | 0-20 |
| `humidity` | float32 | Relative humidity (%) | 10-95 |
| `load_percentage` | float32 | Equipment load (%) | 30-100 |

### Location Data Columns

| Column | Type | Description |
|--------|------|-------------|
| `equipment_id` | string | Equipment identifier |
| `substation` | string | Parent substation |
| `latitude` | float64 | Geographic latitude |
| `longitude` | float64 | Geographic longitude |
| `equipment_type` | string | Type of equipment |
| `capacity_mw` | int | Capacity in MW |
| `installation_year` | int | Year installed |

## Degradation Patterns

### Normal Operation (95%)
- Stable sensor readings with normal variation
- Load following daily patterns
- Minimal sensor drift

### Pre-Failure Degradation (5%)
- Gradual increase in key indicators:
  - Temperature rises
  - Dissolved gas concentrations increase
  - Vibration levels elevate
  - Voltage instability
- Degradation period: 1 week to 1 month before failure
- Exponential progression pattern

### Key Failure Indicators
1. **Dissolved Gas Analysis (DGA)**
   - Acetylene (C2H2) > 100 ppm: Critical
   - Hydrogen (H2) > 200 ppm: Warning
   - Methane (CH4) > 150 ppm: Elevated risk

2. **Temperature**
   - Top oil > 100°C: Critical
   - Top oil > 85°C: Warning

3. **Vibration**
   - Any axis > 8 mm/s: Critical
   - Any axis > 5 mm/s: Warning

## File Format

### Parquet with Snappy Compression

**Benefits:**
- **Compression**: ~10x smaller than CSV
- **Speed**: Fast read/write performance
- **Type-safe**: Preserves data types
- **Columnar**: Efficient for analytics

**Expected sizes:**
- Uncompressed: ~15 GB
- Compressed Parquet: ~1.5-2 GB
- CSV equivalent: ~18 GB

## Usage

### Quick Test (Small Dataset)
```bash
# Test with 10 substations, 1 week of data
python test_generator.py
```

Output: ~8,400 rows (~1 MB)

### Full Generation
```bash
# Generate full 87.6M rows
python data/generate_data.py
```

**Estimated time:**
- Modern laptop: 20-40 minutes
- Server: 10-20 minutes

**Memory usage:**
- Peak: ~2-4 GB RAM
- Uses batch processing to avoid memory issues

### Custom Configuration

Edit `data/generate_data.py`:
```python
# At the bottom of the file
N_SUBSTATIONS = 500  # Change as needed
EQUIPMENT_PER_SUBSTATION = 10  # Change as needed
HOURS = 17520  # 2 years (8760 hours/year)
```

## Loading Data

### Python (Pandas)
```python
import pandas as pd

# Load full dataset
df = pd.read_parquet('data/raw/grid_telemetry_data.parquet')

# Load with filters (efficient!)
df = pd.read_parquet(
    'data/raw/grid_telemetry_data.parquet',
    filters=[('equipment_id', '=', 'SUB001_EQ01')]
)

# Load specific columns
df = pd.read_parquet(
    'data/raw/grid_telemetry_data.parquet',
    columns=['timestamp', 'equipment_id', 'temperature_top']
)
```

### Python (Dask for Large Data)
```python
import dask.dataframe as dd

# Load with Dask for out-of-core processing
ddf = dd.read_parquet('data/raw/grid_telemetry_data.parquet')

# Compute aggregations
result = ddf.groupby('equipment_id')['temperature_top'].mean().compute()
```

### Apache Spark
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("GridGuardian").getOrCreate()
df = spark.read.parquet('data/raw/grid_telemetry_data.parquet')
df.show(5)
```

## Batch Processing

The generator uses batch processing to handle large datasets efficiently:

1. **Batch size**: 168 hours (1 week) per batch
2. **Batches**: 104 batches for 2 years
3. **Progress bar**: Shows generation progress
4. **Memory efficient**: Clears memory after each batch

## Data Quality

### Validation
- All sensor readings within realistic ranges
- No missing values
- Consistent timestamps (hourly)
- Proper equipment ID format

### Statistics
- Mean equipment failure rate: ~5%
- Failing equipment per dataset: ~250 units
- Normal operation: ~95% of data
- Degradation phase: ~5% of data

## Next Steps

After generating data:

1. **Preprocessing**
   ```bash
   python src/preprocessing.py
   ```

2. **Feature Engineering**
   ```bash
   python src/feature_engineering.py
   ```

3. **Model Training**
   ```bash
   python models/train_xgboost.py
   python models/train_lstm.py
   ```

Or run everything:
```bash
python run_pipeline.py
```

## Troubleshooting

### Out of Memory
- Reduce batch size in `generate_and_save_parquet()` method
- Close other applications
- Use 64-bit Python

### Slow Generation
- Check disk space (need ~5 GB free)
- SSD recommended for faster writes
- Disable antivirus scanning temporarily

### Import Errors
```bash
pip install pyarrow fastparquet tqdm pandas numpy
```

## Performance Tips

1. **SSD Storage**: 3-5x faster than HDD
2. **More RAM**: Allows larger batch sizes
3. **Python 3.11+**: Faster execution
4. **Disable indexing**: Turn off file indexing on output folder

## File Structure

```
data/
├── raw/
│   ├── grid_telemetry_data.parquet    # 87.6M rows, ~1.5-2 GB
│   └── equipment_locations.parquet    # 5,000 rows, ~100 KB
└── test/
    └── grid_telemetry_data.parquet    # Test data (if run test_generator.py)
```

## Advanced: Parallel Generation

For even faster generation, split by substation ranges:

```python
# Terminal 1: Substations 1-250
generator = GridDataGenerator(
    n_substations=250,
    equipment_per_substation=10,
    hours=17520
)
generator.generate_and_save_parquet('data/raw/part1')

# Terminal 2: Substations 251-500
# (adjust equipment IDs in code)
```

Then combine:
```python
import pandas as pd
df1 = pd.read_parquet('data/raw/part1/grid_telemetry_data.parquet')
df2 = pd.read_parquet('data/raw/part2/grid_telemetry_data.parquet')
df = pd.concat([df1, df2])
df.to_parquet('data/raw/grid_telemetry_data.parquet')
```

---

**Questions?** Check the README.md or open an issue on GitHub.
