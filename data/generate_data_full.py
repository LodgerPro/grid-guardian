"""
Grid Equipment Data Generator
Generates synthetic sensor data for power grid equipment monitoring

Specifications:
- 500 substations with 10 equipment each = 5,000 objects
- Hourly measurements for 2 years = 17,520 hours
- Total rows: 5,000 × 17,520 = 87,600,000 records
- 95% normal operation, 5% degradation patterns before failure
- Saves as Parquet for efficient compression
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm

np.random.seed(42)


class GridDataGenerator:
    """Generate synthetic grid equipment sensor data for large-scale deployment"""

    def __init__(self, n_substations=500, equipment_per_substation=10, hours=17520):
        """
        Initialize generator

        Args:
            n_substations: Number of substations (default 500)
            equipment_per_substation: Equipment per substation (default 10)
            hours: Number of hours to generate (default 17520 = 2 years)
        """
        self.n_substations = n_substations
        self.equipment_per_substation = equipment_per_substation
        self.n_equipment = n_substations * equipment_per_substation
        self.hours = hours
        self.total_rows = self.n_equipment * self.hours

        print(f"Configuration:")
        print(f"  Substations: {n_substations}")
        print(f"  Equipment per substation: {equipment_per_substation}")
        print(f"  Total equipment: {self.n_equipment:,}")
        print(f"  Hours of data: {hours:,} ({hours/8760:.1f} years)")
        print(f"  Total rows to generate: {self.total_rows:,}")

    def generate_equipment_ids(self):
        """Generate equipment IDs for all substations"""
        equipment_ids = []
        for sub_id in range(1, self.n_substations + 1):
            for eq_id in range(1, self.equipment_per_substation + 1):
                equipment_ids.append(f"SUB{sub_id:03d}_EQ{eq_id:02d}")
        return equipment_ids

    def generate_degradation_pattern(self, equipment_id_idx, total_hours):
        """
        Generate degradation pattern for equipment
        95% normal, 5% degradation before failure
        """
        # Randomly decide if this equipment will have a failure
        will_fail = np.random.random() < 0.05

        if not will_fail:
            # Normal operation throughout
            return np.zeros(total_hours, dtype=np.float32)

        # Failure will occur - create degradation pattern
        failure_hour = np.random.randint(int(total_hours * 0.2), total_hours)
        degradation_start = failure_hour - np.random.randint(168, 720)  # 1 week to 1 month before
        degradation_start = max(0, degradation_start)

        pattern = np.zeros(total_hours, dtype=np.float32)
        # Gradual degradation
        for i in range(degradation_start, failure_hour):
            progress = (i - degradation_start) / (failure_hour - degradation_start)
            pattern[i] = progress ** 2  # Exponential degradation

        # After failure
        pattern[failure_hour:] = 1.0

        return pattern

    def generate_batch_data(self, equipment_ids, start_hour, batch_hours):
        """Generate data for a batch of hours for all equipment"""
        batch_size = len(equipment_ids) * batch_hours
        start_time = datetime(2023, 1, 1) + timedelta(hours=start_hour)

        # Pre-allocate arrays
        timestamps = []
        eq_ids = []

        for hour_offset in range(batch_hours):
            current_time = start_time + timedelta(hours=hour_offset)
            timestamps.extend([current_time] * len(equipment_ids))
            eq_ids.extend(equipment_ids)

        return timestamps, eq_ids

    def generate_sensor_readings(self, n_rows, degradation):
        """
        Generate all sensor readings with degradation patterns

        Args:
            n_rows: Number of rows to generate
            degradation: Array of degradation values (0=normal, 1=failed)

        Returns:
            Dictionary of sensor readings
        """
        # Base load following daily pattern
        hour_of_day = np.arange(n_rows) % 24
        daily_load = 0.6 + 0.3 * np.sin((hour_of_day - 6) * np.pi / 12)
        load_percentage = daily_load + np.random.normal(0, 0.05, n_rows)
        load_percentage = np.clip(load_percentage, 0.3, 1.0)

        # Temperature readings (affected by load and degradation)
        temp_base_top = 65 + 15 * load_percentage + 30 * degradation
        temp_base_oil = 55 + 12 * load_percentage + 25 * degradation
        temperature_top = temp_base_top + np.random.normal(0, 3, n_rows)
        temperature_oil = temp_base_oil + np.random.normal(0, 2, n_rows)

        # Voltage (3-phase)
        voltage_nominal = 230.0
        voltage_variation = np.random.normal(0, 2, n_rows)
        voltage_phase_a = voltage_nominal + voltage_variation - 5 * degradation
        voltage_phase_b = voltage_nominal + voltage_variation - 4 * degradation
        voltage_phase_c = voltage_nominal + voltage_variation - 6 * degradation

        # Current (3-phase, follows load)
        current_base = 400 * load_percentage
        current_phase_a = current_base + np.random.normal(0, 10, n_rows) + 50 * degradation
        current_phase_b = current_base + np.random.normal(0, 10, n_rows) + 45 * degradation
        current_phase_c = current_base + np.random.normal(0, 10, n_rows) + 55 * degradation

        # Dissolved Gas Analysis (DGA) - key failure indicators
        gas_h2 = 50 + 200 * degradation + np.random.normal(0, 10, n_rows)
        gas_ch4 = 30 + 150 * degradation + np.random.normal(0, 8, n_rows)
        gas_c2h2 = 5 + 100 * degradation + np.random.normal(0, 5, n_rows)  # Acetylene critical

        # Vibration (3-axis)
        vibration_base = 2.0
        vibration_x = vibration_base + 5 * degradation + np.random.normal(0, 0.3, n_rows)
        vibration_y = vibration_base + 4 * degradation + np.random.normal(0, 0.3, n_rows)
        vibration_z = vibration_base + 6 * degradation + np.random.normal(0, 0.3, n_rows)

        # Humidity
        humidity = 45 + 20 * degradation + np.random.normal(0, 5, n_rows)

        return {
            'temperature_top': np.clip(temperature_top, 20, 150).astype(np.float32),
            'temperature_oil': np.clip(temperature_oil, 20, 120).astype(np.float32),
            'voltage_phase_a': np.clip(voltage_phase_a, 200, 250).astype(np.float32),
            'voltage_phase_b': np.clip(voltage_phase_b, 200, 250).astype(np.float32),
            'voltage_phase_c': np.clip(voltage_phase_c, 200, 250).astype(np.float32),
            'current_phase_a': np.clip(current_phase_a, 0, 800).astype(np.float32),
            'current_phase_b': np.clip(current_phase_b, 0, 800).astype(np.float32),
            'current_phase_c': np.clip(current_phase_c, 0, 800).astype(np.float32),
            'gas_h2': np.clip(gas_h2, 0, 500).astype(np.float32),
            'gas_ch4': np.clip(gas_ch4, 0, 300).astype(np.float32),
            'gas_c2h2': np.clip(gas_c2h2, 0, 200).astype(np.float32),
            'vibration_x': np.clip(vibration_x, 0, 20).astype(np.float32),
            'vibration_y': np.clip(vibration_y, 0, 20).astype(np.float32),
            'vibration_z': np.clip(vibration_z, 0, 20).astype(np.float32),
            'humidity': np.clip(humidity, 10, 95).astype(np.float32),
            'load_percentage': (load_percentage * 100).astype(np.float32)
        }

    def generate_and_save_parquet(self, output_dir='data/raw'):
        """
        Generate data in batches and save as Parquet files

        Generates data in chunks to avoid memory issues with 87.6M rows
        """
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'grid_telemetry_data.parquet')

        print("\n" + "=" * 70)
        print("Starting large-scale data generation")
        print("=" * 70)

        # Generate equipment IDs
        equipment_ids = self.generate_equipment_ids()
        print(f"\nGenerated {len(equipment_ids)} equipment IDs")

        # Pre-generate degradation patterns for all equipment
        print("\nGenerating degradation patterns for all equipment...")
        degradation_patterns = {}
        failing_equipment = 0

        for idx, eq_id in enumerate(tqdm(equipment_ids, desc="Degradation patterns")):
            pattern = self.generate_degradation_pattern(idx, self.hours)
            degradation_patterns[eq_id] = pattern
            if pattern.max() > 0:
                failing_equipment += 1

        print(f"Equipment with failures: {failing_equipment}/{len(equipment_ids)} ({failing_equipment/len(equipment_ids)*100:.1f}%)")

        # Generate data in batches
        batch_hours = 168  # 1 week at a time
        n_batches = (self.hours + batch_hours - 1) // batch_hours

        print(f"\nGenerating data in {n_batches} batches of {batch_hours} hours each...")

        # Parquet writer
        writer = None
        schema = None
        total_rows_written = 0

        try:
            for batch_idx in tqdm(range(n_batches), desc="Generating batches"):
                start_hour = batch_idx * batch_hours
                end_hour = min(start_hour + batch_hours, self.hours)
                actual_batch_hours = end_hour - start_hour

                # Generate batch
                batch_data = self._generate_batch(
                    equipment_ids,
                    degradation_patterns,
                    start_hour,
                    actual_batch_hours
                )

                # Convert to pandas DataFrame
                df_batch = pd.DataFrame(batch_data)

                # Write to Parquet
                table = pa.Table.from_pandas(df_batch)

                if writer is None:
                    schema = table.schema
                    writer = pq.ParquetWriter(output_file, schema, compression='snappy')

                writer.write_table(table)
                total_rows_written += len(df_batch)

                # Clear memory
                del df_batch, table, batch_data

        finally:
            if writer:
                writer.close()

        print(f"\n[OK] Data generation complete!")
        print(f"  Total rows written: {total_rows_written:,}")
        print(f"  Output file: {output_file}")

        # Get file size
        file_size_bytes = os.path.getsize(output_file)
        file_size_mb = file_size_bytes / (1024 * 1024)
        file_size_gb = file_size_mb / 1024

        if file_size_gb >= 1:
            print(f"  File size: {file_size_gb:.2f} GB")
        else:
            print(f"  File size: {file_size_mb:.2f} MB")

        print(f"  Compression: Snappy")

        return output_file

    def _generate_batch(self, equipment_ids, degradation_patterns, start_hour, batch_hours):
        """Generate a batch of data for all equipment"""
        batch_size = len(equipment_ids) * batch_hours
        start_time = datetime(2023, 1, 1) + timedelta(hours=start_hour)

        # Initialize data structure
        data = {
            'timestamp': [],
            'equipment_id': [],
        }

        # Generate for each equipment
        for eq_id in equipment_ids:
            # Get degradation values for this time period
            degradation = degradation_patterns[eq_id][start_hour:start_hour + batch_hours]

            # Generate timestamps for this equipment
            for hour_offset in range(batch_hours):
                current_time = start_time + timedelta(hours=hour_offset)
                data['timestamp'].append(current_time)
                data['equipment_id'].append(eq_id)

        # Now generate sensor readings for the entire batch
        batch_size = len(data['timestamp'])
        degradation_array = np.array([
            degradation_patterns[eq_id][start_hour + (i % batch_hours)]
            for i, eq_id in enumerate(data['equipment_id'])
        ])

        # Generate all sensor readings
        sensors = self.generate_sensor_readings(batch_size, degradation_array)

        # Merge sensor data
        data.update(sensors)

        return data


def generate_location_data(n_substations=500, equipment_per_substation=10):
    """Generate grid equipment location data for all substations"""
    print("\nGenerating location data for substations and equipment...")

    equipment_ids = []
    latitudes = []
    longitudes = []
    substation_names = []
    equipment_types = []
    capacity_mw_list = []
    installation_years = []

    # Generate locations spread across a geographic region (e.g., state-wide grid)
    # Using a grid pattern with some randomness
    base_lat = 40.0
    base_lon = -75.0
    lat_span = 2.0  # degrees
    lon_span = 3.0  # degrees

    # Calculate grid dimensions
    grid_size = int(np.sqrt(n_substations))

    for sub_idx in range(n_substations):
        sub_id = sub_idx + 1
        substation_name = f"SUB{sub_id:03d}"

        # Grid position with randomness
        row = sub_idx // grid_size
        col = sub_idx % grid_size

        sub_lat = base_lat + (row / grid_size) * lat_span + np.random.uniform(-0.05, 0.05)
        sub_lon = base_lon + (col / grid_size) * lon_span + np.random.uniform(-0.05, 0.05)

        # Generate equipment for this substation
        for eq_idx in range(1, equipment_per_substation + 1):
            eq_id = f"SUB{sub_id:03d}_EQ{eq_idx:02d}"

            # Equipment at same substation location (with tiny offset)
            eq_lat = sub_lat + np.random.uniform(-0.001, 0.001)
            eq_lon = sub_lon + np.random.uniform(-0.001, 0.001)

            # Determine equipment type
            if eq_idx <= 3:
                eq_type = 'Power Transformer'
                capacity = np.random.choice([50, 100, 150, 200])
            elif eq_idx <= 6:
                eq_type = 'Distribution Transformer'
                capacity = np.random.choice([10, 25, 50])
            elif eq_idx <= 8:
                eq_type = 'Circuit Breaker'
                capacity = np.random.choice([100, 150, 200])
            else:
                eq_type = 'Voltage Regulator'
                capacity = np.random.choice([50, 75, 100])

            installation_year = np.random.randint(1990, 2023)

            equipment_ids.append(eq_id)
            latitudes.append(eq_lat)
            longitudes.append(eq_lon)
            substation_names.append(substation_name)
            equipment_types.append(eq_type)
            capacity_mw_list.append(capacity)
            installation_years.append(installation_year)

    df = pd.DataFrame({
        'equipment_id': equipment_ids,
        'substation': substation_names,
        'latitude': latitudes,
        'longitude': longitudes,
        'equipment_type': equipment_types,
        'capacity_mw': capacity_mw_list,
        'installation_year': installation_years
    })

    os.makedirs('data/raw', exist_ok=True)
    output_file = 'data/raw/equipment_locations.parquet'
    df.to_parquet(output_file, index=False, compression='snappy')

    print(f"[OK] Location data saved: {len(df):,} equipment locations")
    print(f"  Substations: {n_substations}")
    print(f"  Equipment per substation: {equipment_per_substation}")
    print(f"  Output: {output_file}")

    return df


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "GRID GUARDIAN - DATA GENERATION" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Configuration
    N_SUBSTATIONS = 500
    EQUIPMENT_PER_SUBSTATION = 10
    HOURS = 17520  # 2 years

    # Generate telemetry data
    print("📊 TELEMETRY DATA GENERATION")
    generator = GridDataGenerator(
        n_substations=N_SUBSTATIONS,
        equipment_per_substation=EQUIPMENT_PER_SUBSTATION,
        hours=HOURS
    )

    telemetry_file = generator.generate_and_save_parquet('data/raw')

    # Generate location data
    print("\n" + "=" * 70)
    print("📍 LOCATION DATA GENERATION")
    location_df = generate_location_data(N_SUBSTATIONS, EQUIPMENT_PER_SUBSTATION)

    # Summary
    print("\n" + "=" * 70)
    print("[OK] DATA GENERATION COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  1. Telemetry: {telemetry_file}")
    print(f"  2. Locations: data/raw/equipment_locations.parquet")
    print("\nNext steps:")
    print("  - Run preprocessing: python src/preprocessing.py")
    print("  - Or run full pipeline: python run_pipeline.py")
    print("=" * 70 + "\n")
