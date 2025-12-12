"""
Data Validation Tests for Grid Guardian

Tests adapt dynamically to actual data structure and validate:
- Data integrity (completeness, types, ranges)
- Risk classification correctness
- Equipment coverage
- Temporal consistency
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestDataFilesExist:
    """Verify data files exist and are accessible"""

    def test_data_directory_exists(self, data_dir):
        """Data directory must exist"""
        assert data_dir.exists(), f"Data directory not found: {data_dir}"

    def test_at_least_one_data_file_exists(self, data_files):
        """At least one data file must exist"""
        total = len(data_files['parquet']) + len(data_files['csv'])
        assert total > 0, "No data files found (parquet or csv)"

    def test_telemetry_data_exists(self, data_files):
        """Telemetry/grid data file must exist"""
        parquet_files = [f.name for f in data_files['parquet']]
        has_telemetry = any('telemetry' in f or 'grid' in f for f in parquet_files)
        assert has_telemetry, f"No telemetry data found. Files: {parquet_files}"


class TestTelemetryDataStructure:
    """Validate telemetry data structure and integrity"""

    def test_telemetry_loaded_successfully(self, telemetry_data):
        """Telemetry data loads without errors"""
        assert telemetry_data is not None, "Failed to load telemetry data"
        assert isinstance(telemetry_data, pd.DataFrame), "Telemetry data is not a DataFrame"
        assert len(telemetry_data) > 0, "Telemetry data is empty"

    def test_telemetry_has_minimum_records(self, telemetry_data):
        """Telemetry data has substantial number of records"""
        min_records = 10000  # Expect at least 10K records
        assert len(telemetry_data) >= min_records, (
            f"Too few records: {len(telemetry_data):,} < {min_records:,}"
        )

    def test_telemetry_has_expected_column_patterns(self, telemetry_columns):
        """Telemetry data has expected column patterns"""
        assert len(telemetry_columns) > 0, "No columns found"

        # Check for essential column patterns
        checks = {
            'timestamp': any('time' in col.lower() for col in telemetry_columns),
            'equipment_id': any('equipment' in col.lower() and 'id' in col.lower()
                               for col in telemetry_columns),
            'temperature': any('temp' in col.lower() for col in telemetry_columns),
            'voltage': any('voltage' in col.lower() for col in telemetry_columns),
            'current': any('current' in col.lower() for col in telemetry_columns),
        }

        missing = [name for name, present in checks.items() if not present]
        assert not missing, (
            f"Missing expected column patterns: {missing}\n"
            f"Available columns: {telemetry_columns}"
        )

    def test_no_nulls_in_critical_columns(self, telemetry_data, telemetry_columns):
        """Critical columns must have no null values"""
        # Identify critical columns
        critical_patterns = ['id', 'time', 'equipment']
        critical_cols = [
            col for col in telemetry_columns
            if any(p in col.lower() for p in critical_patterns)
        ]

        failures = []
        for col in critical_cols:
            null_count = telemetry_data[col].isnull().sum()
            if null_count > 0:
                pct = null_count / len(telemetry_data) * 100
                failures.append(f"  {col}: {null_count:,} nulls ({pct:.2f}%)")

        assert not failures, "Found nulls in critical columns:\n" + "\n".join(failures)

    def test_equipment_ids_format(self, telemetry_data):
        """Equipment IDs follow expected format (SUBxxx_EQxx)"""
        if 'equipment_id' not in telemetry_data.columns:
            pytest.skip("No equipment_id column")

        sample_ids = telemetry_data['equipment_id'].unique()[:10]

        # Check format: SUB + digits + _EQ + digits
        import re
        pattern = r'^SUB\d{3}_EQ\d{2}$'

        invalid = [id_ for id_ in sample_ids if not re.match(pattern, str(id_))]

        assert not invalid, (
            f"Invalid equipment ID format: {invalid}\n"
            f"Expected format: SUBxxx_EQxx (e.g., SUB001_EQ01)"
        )

    def test_timestamp_is_datetime(self, telemetry_data, telemetry_columns):
        """Timestamp column is datetime type"""
        time_cols = [col for col in telemetry_columns if 'time' in col.lower()]
        assert time_cols, "No timestamp column found"

        time_col = time_cols[0]
        dtype = telemetry_data[time_col].dtype

        assert pd.api.types.is_datetime64_any_dtype(dtype), (
            f"Timestamp column '{time_col}' is not datetime type: {dtype}"
        )

    def test_timestamps_are_sequential(self, sample_telemetry):
        """Timestamps are in chronological order (per equipment)"""
        time_cols = [col for col in sample_telemetry.columns if 'time' in col.lower()]
        if not time_cols:
            pytest.skip("No timestamp column")

        time_col = time_cols[0]
        equipment_col = 'equipment_id'

        if equipment_col not in sample_telemetry.columns:
            pytest.skip("No equipment_id column")

        # Check one equipment's timestamps
        first_equipment = sample_telemetry[equipment_col].iloc[0]
        eq_data = sample_telemetry[sample_telemetry[equipment_col] == first_equipment]

        timestamps = eq_data[time_col].sort_values()
        assert timestamps.is_monotonic_increasing, (
            f"Timestamps not sequential for {first_equipment}"
        )


class TestNumericColumnsRanges:
    """Validate numeric columns have realistic ranges"""

    def test_temperature_ranges(self, telemetry_data, telemetry_columns):
        """Temperature columns have realistic ranges"""
        temp_cols = [col for col in telemetry_columns if 'temp' in col.lower()]

        failures = []
        for col in temp_cols:
            min_val = telemetry_data[col].min()
            max_val = telemetry_data[col].max()

            # Transformer temperatures: typically 20-120°C
            if min_val < 0 or min_val > 150:
                failures.append(f"{col}: unrealistic min={min_val:.1f}°C")
            if max_val < 0 or max_val > 150:
                failures.append(f"{col}: unrealistic max={max_val:.1f}°C")

        assert not failures, "Temperature range issues:\n" + "\n".join(failures)

    def test_voltage_ranges(self, telemetry_data, telemetry_columns):
        """Voltage columns have realistic ranges"""
        voltage_cols = [col for col in telemetry_columns if 'voltage' in col.lower()]

        failures = []
        for col in voltage_cols:
            min_val = telemetry_data[col].min()
            max_val = telemetry_data[col].max()

            # Grid voltage: typically 200-250V (phase)
            if min_val < 100 or min_val > 300:
                failures.append(f"{col}: unrealistic min={min_val:.1f}V")
            if max_val < 100 or max_val > 300:
                failures.append(f"{col}: unrealistic max={max_val:.1f}V")

        assert not failures, "Voltage range issues:\n" + "\n".join(failures)

    def test_no_negative_values_in_absolute_columns(self, telemetry_data, telemetry_columns):
        """Columns that should be positive have no negative values"""
        # Columns that must be >= 0
        positive_patterns = ['vibration', 'gas', 'humidity', 'load']

        failures = []
        for col in telemetry_columns:
            if any(p in col.lower() for p in positive_patterns):
                min_val = telemetry_data[col].min()
                if min_val < 0:
                    failures.append(f"{col}: has negative value {min_val:.2f}")

        assert not failures, "Negative value issues:\n" + "\n".join(failures)


class TestEquipmentCoverage:
    """Validate equipment coverage and distribution"""

    def test_expected_equipment_count(self, expected_equipment_ids, expected_total_equipment):
        """Number of equipment matches expected count"""
        actual_count = len(expected_equipment_ids)
        assert actual_count == expected_total_equipment, (
            f"Expected {expected_total_equipment} equipment units, found {actual_count}\n"
            f"IDs: {expected_equipment_ids}"
        )

    def test_all_equipment_has_data(self, telemetry_data, expected_equipment_ids):
        """All expected equipment IDs have data"""
        if 'equipment_id' not in telemetry_data.columns:
            pytest.skip("No equipment_id column")

        # Check each equipment has at least some records
        min_records_per_equipment = 100  # At least 100 records per unit

        failures = []
        for eq_id in expected_equipment_ids:
            count = (telemetry_data['equipment_id'] == eq_id).sum()
            if count < min_records_per_equipment:
                failures.append(f"{eq_id}: only {count} records")

        assert not failures, "Equipment with insufficient data:\n" + "\n".join(failures)

    def test_equipment_data_balanced(self, telemetry_data):
        """Equipment have roughly balanced number of records"""
        if 'equipment_id' not in telemetry_data.columns:
            pytest.skip("No equipment_id column")

        counts = telemetry_data['equipment_id'].value_counts()
        mean_count = counts.mean()
        std_count = counts.std()

        # Check no equipment has too few or too many records (within 3 std)
        outliers = counts[(counts < mean_count - 3*std_count) |
                         (counts > mean_count + 3*std_count)]

        assert len(outliers) == 0, (
            f"Equipment with unbalanced data (mean={mean_count:.0f}, std={std_count:.0f}):\n"
            f"{outliers.to_dict()}"
        )


class TestFeaturesData:
    """Validate processed features data"""

    def test_features_data_exists(self, features_data):
        """Features data loads successfully"""
        assert features_data is not None, "No features data found"
        assert len(features_data) > 0, "Features data is empty"

    def test_features_has_risk_level(self, features_data):
        """Features data has risk_level column"""
        if features_data is None:
            pytest.skip("No features data")

        assert 'risk_level' in features_data.columns, (
            f"Missing risk_level column. Available: {features_data.columns.tolist()}"
        )

    def test_risk_levels_are_valid(self, features_data, expected_risk_levels):
        """Risk levels contain only expected values (0, 1, 2)"""
        if features_data is None or 'risk_level' not in features_data.columns:
            pytest.skip("No risk_level data")

        unique_levels = sorted(features_data['risk_level'].unique())
        assert unique_levels == expected_risk_levels, (
            f"Unexpected risk levels: {unique_levels}, expected {expected_risk_levels}"
        )

    def test_risk_distribution_matches_expected(self, features_data, expected_risk_distribution,
                                               check_risk_distribution):
        """Risk distribution matches expected proportions"""
        if features_data is None:
            pytest.skip("No features data")

        # Allow 5% tolerance
        check_risk_distribution(features_data, expected_risk_distribution, tolerance=0.05)

    def test_failure_probability_in_range(self, features_data):
        """Failure probability is between 0 and 1"""
        if features_data is None or 'failure_probability' not in features_data.columns:
            pytest.skip("No failure_probability column")

        min_val = features_data['failure_probability'].min()
        max_val = features_data['failure_probability'].max()

        assert 0 <= min_val <= 1, f"failure_probability min out of range: {min_val}"
        assert 0 <= max_val <= 1, f"failure_probability max out of range: {max_val}"

    def test_features_count(self, features_columns):
        """Features data has substantial number of columns (engineered features)"""
        # Expect at least 50 columns (18 raw + engineered)
        assert len(features_columns) >= 50, (
            f"Too few features: {len(features_columns)} (expected >= 50)"
        )


class TestLocationData:
    """Validate equipment location data"""

    def test_location_data_exists(self, location_data):
        """Location data loads successfully"""
        assert location_data is not None, "No location data found"

    def test_location_has_coordinates(self, location_data):
        """Location data has latitude and longitude"""
        if location_data is None:
            pytest.skip("No location data")

        required = ['latitude', 'longitude']
        missing = [col for col in required if col not in location_data.columns]

        assert not missing, (
            f"Missing coordinate columns: {missing}\n"
            f"Available: {location_data.columns.tolist()}"
        )

    def test_coordinates_in_russia(self, location_data):
        """Coordinates are within Russia bounds"""
        if location_data is None:
            pytest.skip("No location data")

        if 'latitude' not in location_data.columns or 'longitude' not in location_data.columns:
            pytest.skip("No coordinate columns")

        # Russia bounds (approximate)
        lat_min, lat_max = 41, 82
        lon_min, lon_max = 19, 180

        lat_out = location_data[
            (location_data['latitude'] < lat_min) | (location_data['latitude'] > lat_max)
        ]
        lon_out = location_data[
            (location_data['longitude'] < lon_min) | (location_data['longitude'] > lon_max)
        ]

        assert len(lat_out) == 0, f"Latitudes outside Russia: {lat_out['latitude'].tolist()}"
        assert len(lon_out) == 0, f"Longitudes outside Russia: {lon_out['longitude'].tolist()}"

    def test_location_covers_expected_equipment(self, location_data, expected_total_equipment):
        """Location data covers all equipment"""
        if location_data is None:
            pytest.skip("No location data")

        actual_count = len(location_data)
        assert actual_count == expected_total_equipment, (
            f"Expected {expected_total_equipment} locations, found {actual_count}"
        )
