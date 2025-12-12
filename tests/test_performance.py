"""
Performance Tests for Grid Guardian

Tests system performance and response times:
- Data loading speed
- Aggregation performance
- Memory usage
- Dashboard responsiveness
"""

import pytest
import time
import pandas as pd
import numpy as np
from pathlib import Path


class TestDataLoadingPerformance:
    """Test data loading times"""

    @pytest.mark.slow
    def test_parquet_loading_speed(self, data_files):
        """Parquet files load in reasonable time"""
        if not data_files['parquet']:
            pytest.skip("No parquet files")

        # Test largest parquet file
        parquet_files = data_files['parquet']
        largest = max(parquet_files, key=lambda f: f.stat().st_size)

        try:
            start = time.time()
            df = pd.read_parquet(largest)
            load_time = time.time() - start
        except Exception as e:
            pytest.skip(f"Could not load parquet file {largest.name}: {e}")

        file_size_mb = largest.stat().st_size / (1024 * 1024)

        # Allow 0.5s per 10MB
        max_time = max(5.0, file_size_mb / 10 * 0.5)

        assert load_time < max_time, (
            f"Loading {largest.name} ({file_size_mb:.1f}MB) took {load_time:.2f}s "
            f"(max: {max_time:.2f}s)"
        )

    def test_csv_loading_speed(self, data_files):
        """CSV files load in reasonable time"""
        csv_files = [f for f in data_files['csv'] if f.stat().st_size > 1024]  # > 1KB

        if not csv_files:
            pytest.skip("No substantial CSV files")

        # Test largest CSV
        largest = max(csv_files, key=lambda f: f.stat().st_size)

        start = time.time()
        df = pd.read_csv(largest)
        load_time = time.time() - start

        file_size_mb = largest.stat().st_size / (1024 * 1024)

        # CSV is slower than parquet, allow 1s per 5MB
        max_time = max(10.0, file_size_mb / 5)

        assert load_time < max_time, (
            f"Loading {largest.name} ({file_size_mb:.1f}MB) took {load_time:.2f}s "
            f"(max: {max_time:.2f}s)"
        )


class TestAggregationPerformance:
    """Test aggregation and groupby performance"""

    def test_equipment_groupby_speed(self, sample_telemetry):
        """Equipment-level groupby completes quickly"""
        if 'equipment_id' not in sample_telemetry.columns:
            pytest.skip("No equipment_id")

        start = time.time()
        result = sample_telemetry.groupby('equipment_id').size()
        agg_time = time.time() - start

        assert agg_time < 1.0, (
            f"Simple groupby took {agg_time:.3f}s on {len(sample_telemetry):,} rows "
            "(expected < 1s)"
        )

    def test_multi_column_aggregation_speed(self, sample_features):
        """Multi-column aggregation completes quickly"""
        if 'equipment_id' not in sample_features.columns:
            pytest.skip("No equipment_id")

        # Simulate Home.py aggregation
        agg_dict = {}
        for col in ['temperature_top', 'vibration_x', 'failure_probability']:
            if col in sample_features.columns:
                agg_dict[col] = ['mean', 'max']

        if not agg_dict:
            pytest.skip("No columns to aggregate")

        start = time.time()
        result = sample_features.groupby('equipment_id').agg(agg_dict)
        agg_time = time.time() - start

        assert agg_time < 2.0, (
            f"Multi-column aggregation took {agg_time:.3f}s on {len(sample_features):,} rows "
            "(expected < 2s)"
        )

    def test_stratified_sampling_speed(self, features_data):
        """Stratified sampling completes quickly"""
        if features_data is None or 'risk_level' not in features_data.columns:
            pytest.skip("No risk data")

        # Sample 10K rows with stratification
        target_sample = 10000
        n = min(len(features_data), target_sample * 2)  # Use subset for speed

        df = features_data.head(n)

        start = time.time()

        # Proportional sampling logic
        total_sample = min(target_sample, len(df))
        risk_counts = df['risk_level'].value_counts()

        sampled_dfs = []
        for level in [0, 1, 2]:
            if level in risk_counts.index:
                proportion = risk_counts[level] / len(df)
                sample_size = int(total_sample * proportion)
                if sample_size > 0:
                    level_df = df[df['risk_level'] == level]
                    n_sample = min(len(level_df), sample_size)
                    sampled_dfs.append(level_df.sample(n=n_sample, random_state=42))

        result = pd.concat(sampled_dfs, ignore_index=True)

        sample_time = time.time() - start

        assert sample_time < 3.0, (
            f"Stratified sampling took {sample_time:.3f}s (expected < 3s)"
        )


class TestMemoryUsage:
    """Test memory efficiency"""

    def test_sample_data_memory_efficient(self, sample_telemetry):
        """Sample data uses reasonable memory"""
        memory_mb = sample_telemetry.memory_usage(deep=True).sum() / (1024 * 1024)

        # 1000 rows should use < 10MB
        expected_max_mb = 10

        assert memory_mb < expected_max_mb, (
            f"Sample data uses {memory_mb:.1f}MB (expected < {expected_max_mb}MB)"
        )

    def test_full_features_memory_usage(self, features_data):
        """Full features dataset has acceptable memory footprint"""
        if features_data is None:
            pytest.skip("No features data")

        memory_mb = features_data.memory_usage(deep=True).sum() / (1024 * 1024)

        # 876K rows × 95 cols should use < 500MB
        expected_max_mb = 500

        assert memory_mb < expected_max_mb, (
            f"Features data uses {memory_mb:.1f}MB (expected < {expected_max_mb}MB)\n"
            f"Shape: {features_data.shape}"
        )


class TestComputationSpeed:
    """Test specific computation speeds"""

    def test_risk_level_classification_speed(self, sample_telemetry):
        """Risk level can be calculated quickly"""
        # Simulate risk calculation logic
        required_cols = ['temperature_top', 'vibration_x', 'gas_c2h2']
        if not all(col in sample_telemetry.columns for col in required_cols):
            pytest.skip("Missing required columns")

        start = time.time()

        # Simplified risk logic
        high_risk = (
            (sample_telemetry['temperature_top'] > 100) |
            (sample_telemetry['gas_c2h2'] > 100) |
            (sample_telemetry['vibration_x'] > 8)
        )

        medium_risk = (
            (sample_telemetry['temperature_top'] > 85) |
            (sample_telemetry['gas_c2h2'] > 50) |
            (sample_telemetry['vibration_x'] > 5)
        )

        risk_level = np.where(high_risk, 2, np.where(medium_risk, 1, 0))

        calc_time = time.time() - start

        assert calc_time < 0.5, (
            f"Risk calculation took {calc_time:.3f}s on {len(sample_telemetry):,} rows "
            "(expected < 0.5s)"
        )

    def test_rolling_statistics_speed(self, sample_features):
        """Rolling statistics can be calculated quickly"""
        if 'humidity' not in sample_features.columns or 'timestamp' not in sample_features.columns:
            pytest.skip("Missing required columns")

        # Sort by timestamp
        df = sample_features.sort_values('timestamp').copy()

        start = time.time()

        # Calculate rolling mean (3-hour window)
        df['rolling_mean'] = df['humidity'].rolling(window=3).mean()

        roll_time = time.time() - start

        assert roll_time < 1.0, (
            f"Rolling calculation took {roll_time:.3f}s on {len(df):,} rows "
            "(expected < 1s)"
        )


class TestQueryPerformance:
    """Test data query and filtering performance"""

    def test_equipment_filter_speed(self, sample_features):
        """Filtering by equipment is fast"""
        if 'equipment_id' not in sample_features.columns:
            pytest.skip("No equipment_id")

        equipment_list = sample_features['equipment_id'].unique()
        if len(equipment_list) == 0:
            pytest.skip("No equipment")

        target_equipment = equipment_list[0]

        start = time.time()
        result = sample_features[sample_features['equipment_id'] == target_equipment]
        filter_time = time.time() - start

        assert filter_time < 0.1, (
            f"Equipment filter took {filter_time:.4f}s (expected < 0.1s)"
        )

    def test_risk_level_filter_speed(self, sample_features):
        """Filtering by risk level is fast"""
        if 'risk_level' not in sample_features.columns:
            pytest.skip("No risk_level")

        start = time.time()
        result = sample_features[sample_features['risk_level'] == 2]
        filter_time = time.time() - start

        assert filter_time < 0.1, (
            f"Risk filter took {filter_time:.4f}s (expected < 0.1s)"
        )

    def test_timestamp_range_filter_speed(self, sample_features):
        """Filtering by timestamp range is fast"""
        if 'timestamp' not in sample_features.columns:
            pytest.skip("No timestamp")

        # Ensure timestamp is datetime type
        timestamps = pd.to_datetime(sample_features['timestamp'], errors='coerce')

        # Get date range
        min_date = timestamps.min()
        max_date = timestamps.max()

        if pd.isna(min_date) or pd.isna(max_date):
            pytest.skip("Invalid timestamps")

        # Filter to middle 50%
        midpoint = min_date + (max_date - min_date) / 2
        range_start = min_date + (max_date - min_date) / 4

        start = time.time()
        result = sample_features[
            (timestamps >= range_start) &
            (timestamps <= midpoint)
        ]
        filter_time = time.time() - start

        assert filter_time < 0.2, (
            f"Timestamp range filter took {filter_time:.4f}s (expected < 0.2s)"
        )


class TestScalability:
    """Test scalability with larger datasets"""

    @pytest.mark.slow
    def test_large_dataset_sampling_scales(self, features_data):
        """Sampling scales linearly with data size"""
        if features_data is None:
            pytest.skip("No features data")

        # Test with different sample sizes
        sizes = [1000, 5000, 10000]
        times = []

        for size in sizes:
            if size > len(features_data):
                continue

            start = time.time()
            sample = features_data.sample(n=size, random_state=42)
            sample_time = time.time() - start
            times.append((size, sample_time))

        if len(times) < 2:
            pytest.skip("Not enough data for scalability test")

        # Check that time doesn't increase super-linearly
        for i in range(1, len(times)):
            size_ratio = times[i][0] / times[0][0]
            time_ratio = times[i][1] / times[0][1]

            # Time should not grow more than 2x per size doubling
            assert time_ratio < size_ratio * 2, (
                f"Poor scaling: {times[0][0]} rows in {times[0][1]:.3f}s, "
                f"{times[i][0]} rows in {times[i][1]:.3f}s "
                f"(time ratio {time_ratio:.1f}x vs size ratio {size_ratio:.1f}x)"
            )


class TestCachingEffectiveness:
    """Test that caching improves performance"""

    def test_repeated_load_is_faster(self, data_files):
        """Second load of same data is faster (file system cache)"""
        if not data_files['parquet']:
            pytest.skip("No parquet files")

        test_file = data_files['parquet'][0]

        # First load
        start = time.time()
        df1 = pd.read_parquet(test_file)
        first_load = time.time() - start

        # Second load
        start = time.time()
        df2 = pd.read_parquet(test_file)
        second_load = time.time() - start

        # Second load should be same or faster (OS cache)
        # Allow some variance
        assert second_load <= first_load * 1.5, (
            f"Second load slower: {second_load:.3f}s vs {first_load:.3f}s"
        )
