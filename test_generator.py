"""
Quick test of data generator with small dataset
For testing without generating full 87.6M rows
"""

import sys
sys.path.append('.')

from data.generate_data import GridDataGenerator, generate_location_data

print("=" * 70)
print("TESTING DATA GENERATOR WITH SMALL DATASET")
print("=" * 70)

# Test with 10 substations, 5 equipment each, 2 years of data
N_SUBSTATIONS = 10
EQUIPMENT_PER_SUBSTATION = 5
HOURS = 17520  # 2 years (24 * 365 * 2)

print(f"\nTest configuration:")
print(f"  Substations: {N_SUBSTATIONS}")
print(f"  Equipment per substation: {EQUIPMENT_PER_SUBSTATION}")
print(f"  Total equipment: {N_SUBSTATIONS * EQUIPMENT_PER_SUBSTATION}")
print(f"  Hours: {HOURS} (1 week)")
print(f"  Expected rows: {N_SUBSTATIONS * EQUIPMENT_PER_SUBSTATION * HOURS:,}")

# Generate data
generator = GridDataGenerator(
    n_substations=N_SUBSTATIONS,
    equipment_per_substation=EQUIPMENT_PER_SUBSTATION,
    hours=HOURS
)

output_file = generator.generate_and_save_parquet('data/test')

# Generate location data
print("\n" + "=" * 70)
location_df = generate_location_data(N_SUBSTATIONS, EQUIPMENT_PER_SUBSTATION)

# Load and verify
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

import pandas as pd

df = pd.read_parquet('data/test/grid_telemetry_data.parquet')
print(f"\n[OK] Successfully loaded {len(df):,} rows")
print(f"\nColumns ({len(df.columns)}):")
for col in df.columns:
    print(f"  - {col}: {df[col].dtype}")

print(f"\nSample data (first 3 rows):")
print(df.head(3))

print(f"\nData types:")
print(df.dtypes)

print(f"\nMemory usage:")
print(f"  DataFrame: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print("\n" + "=" * 70)
print("[OK] TEST COMPLETED SUCCESSFULLY!")
print("=" * 70)
print("\nReady to generate full dataset with:")
print("  python data/generate_data.py")
print("=" * 70)
