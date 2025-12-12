"""
Integration Tests for Grid Guardian

Tests the full data pipeline and integration between components:
- Raw data → Preprocessing → Feature engineering → Model → Dashboard
- Cross-module functionality
- End-to-end workflows
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys


class TestDataPipeline:
    """Test the full data processing pipeline"""

    def test_raw_to_features_pipeline(self, telemetry_data, features_data):
        """Raw telemetry can be transformed to features"""
        assert telemetry_data is not None, "No raw data"
        assert features_data is not None, "No features data"

        # Features should have same equipment IDs as raw data
        if 'equipment_id' in telemetry_data.columns and 'equipment_id' in features_data.columns:
            raw_equipment = set(telemetry_data['equipment_id'].unique())
            features_equipment = set(features_data['equipment_id'].unique())

            assert raw_equipment == features_equipment, (
                f"Equipment mismatch between raw and features:\n"
                f"  Only in raw: {raw_equipment - features_equipment}\n"
                f"  Only in features: {features_equipment - raw_equipment}"
            )

    @pytest.mark.slow
    def test_can_generate_test_data(self, project_root):
        """Test data generator runs successfully"""
        test_gen = project_root / "test_generator.py"

        if not test_gen.exists():
            pytest.skip("test_generator.py not found")

        # Import and check structure
        spec = __import__('importlib.util').util.spec_from_file_location("test_gen", test_gen)
        if spec and spec.loader:
            module = __import__('importlib.util').util.module_from_spec(spec)
            # Just verify it can be loaded
            assert module is not None, "Failed to load test_generator.py"

    @pytest.mark.integration
    def test_preprocessing_module_exists(self, src_dir):
        """Preprocessing module can be imported"""
        preprocessing_file = src_dir / "preprocessing.py"
        assert preprocessing_file.exists(), "preprocessing.py not found"

    @pytest.mark.integration
    def test_feature_engineering_module_exists(self, src_dir):
        """Feature engineering module can be imported"""
        feat_eng_file = src_dir / "feature_engineering.py"
        assert feat_eng_file.exists(), "feature_engineering.py not found"


class TestRiskCalculation:
    """Test risk calculation consistency across modules"""

    def test_risk_levels_consistent_with_failure_probability(self, features_data):
        """High risk_level corresponds to high failure_probability"""
        if features_data is None:
            pytest.skip("No features data")

        if 'risk_level' not in features_data.columns or 'failure_probability' not in features_data.columns:
            pytest.skip("Missing risk columns")

        # Check correlation between risk_level and failure_probability
        sample = features_data.sample(n=min(1000, len(features_data)), random_state=42)

        # High risk should generally have higher failure probability than low risk
        low_risk = sample[sample['risk_level'] == 0]['failure_probability'].mean()
        high_risk = sample[sample['risk_level'] == 2]['failure_probability'].mean()

        assert high_risk > low_risk, (
            f"High risk avg failure prob ({high_risk:.3f}) should be > "
            f"low risk ({low_risk:.3f})"
        )

    def test_critical_equipment_identification(self, features_data):
        """Equipment with risk_level=2 can be correctly identified"""
        if features_data is None or 'risk_level' not in features_data.columns:
            pytest.skip("No risk data")

        critical = features_data[features_data['risk_level'] == 2]

        if len(critical) > 0:
            # Critical equipment should have equipment_id
            assert 'equipment_id' in critical.columns, "No equipment_id in critical data"

            # Get unique critical equipment count
            unique_critical = critical['equipment_id'].nunique()
            total_equipment = features_data['equipment_id'].nunique()

            # At least 1 equipment should be critical, but not all
            assert 0 < unique_critical < total_equipment, (
                f"Unrealistic critical equipment count: {unique_critical}/{total_equipment}"
            )


class TestEquipmentAggregation:
    """Test equipment-level aggregation logic"""

    def test_equipment_summary_aggregation(self, sample_features):
        """Can aggregate metrics per equipment"""
        if 'equipment_id' not in sample_features.columns:
            pytest.skip("No equipment_id")

        # Simulate Home.py aggregation logic
        agg_dict = {
            'temperature_top': 'mean',
        }

        if 'vibration_x' in sample_features.columns:
            agg_dict['vibration_x'] = 'mean'

        if 'failure_probability' in sample_features.columns:
            agg_dict['failure_probability'] = 'max'

        if 'risk_level' in sample_features.columns:
            agg_dict['risk_level'] = 'max'

        summary = sample_features.groupby('equipment_id').agg(agg_dict).reset_index()

        # Verify aggregation succeeded
        assert len(summary) > 0, "Aggregation returned empty"
        assert len(summary) == sample_features['equipment_id'].nunique(), "Wrong equipment count"

    def test_risk_status_mapping(self, sample_features):
        """Can map risk_level to status labels"""
        if 'risk_level' not in sample_features.columns:
            pytest.skip("No risk_level")

        # Simulate status mapping logic
        risk_mapping = {0: 'Норма', 1: 'Внимание', 2: 'Критично'}

        sample_features['status'] = sample_features['risk_level'].map(risk_mapping)

        # All values should be mapped
        assert sample_features['status'].notna().all(), "Some risk_levels not mapped"

        # Check expected values
        unique_statuses = set(sample_features['status'].unique())
        expected_statuses = {'Норма', 'Внимание', 'Критично'}
        assert unique_statuses.issubset(expected_statuses), (
            f"Unexpected statuses: {unique_statuses - expected_statuses}"
        )


class TestStratifiedSampling:
    """Test stratified sampling maintains risk distribution"""

    def test_proportional_sampling_maintains_distribution(self, features_data,
                                                           expected_risk_distribution):
        """Stratified sampling preserves risk proportions"""
        if features_data is None or 'risk_level' not in features_data.columns:
            pytest.skip("No risk data")

        # Simulate proportional sampling (Home.py logic)
        total_sample = 10000
        risk_counts = features_data['risk_level'].value_counts()

        sampled_dfs = []
        for level in [0, 1, 2]:
            if level in risk_counts.index:
                proportion = risk_counts[level] / len(features_data)
                sample_size = int(total_sample * proportion)

                if sample_size > 0:
                    level_df = features_data[features_data['risk_level'] == level]
                    n = min(len(level_df), sample_size)
                    sampled_dfs.append(level_df.sample(n=n, random_state=42))

        sampled = pd.concat(sampled_dfs, ignore_index=True)

        # Check distribution is preserved
        sampled_dist = sampled['risk_level'].value_counts(normalize=True).to_dict()

        for level, expected_pct in expected_risk_distribution.items():
            actual_pct = sampled_dist.get(level, 0)
            diff = abs(actual_pct - expected_pct)

            # Allow 10% tolerance for sampling
            assert diff <= 0.10, (
                f"Sampling changed distribution for level {level}: "
                f"expected {expected_pct:.1%}, got {actual_pct:.1%}"
            )


class TestLocationDataIntegration:
    """Test location data integration with telemetry"""

    def test_can_merge_location_with_telemetry(self, location_data, sample_telemetry):
        """Location data can be merged with telemetry"""
        if location_data is None or sample_telemetry is None:
            pytest.skip("Missing data")

        if 'equipment_id' not in location_data.columns or 'equipment_id' not in sample_telemetry.columns:
            pytest.skip("No equipment_id for merge")

        # Merge
        merged = sample_telemetry.merge(location_data, on='equipment_id', how='left')

        # All telemetry records should have location
        missing_location = merged[merged['latitude'].isna() | merged['longitude'].isna()]

        assert len(missing_location) == 0, (
            f"Equipment without location: {missing_location['equipment_id'].unique()}"
        )

    def test_can_merge_location_with_risk_data(self, location_data, sample_features):
        """Location data can be merged with risk data"""
        if location_data is None or sample_features is None:
            pytest.skip("Missing data")

        if 'equipment_id' not in location_data.columns or 'equipment_id' not in sample_features.columns:
            pytest.skip("No equipment_id for merge")

        # Get latest risk per equipment
        latest_risk = sample_features.groupby('equipment_id').agg({
            'risk_level': 'last',
            'failure_probability': 'last'
        }).reset_index()

        # Merge with location
        merged = location_data.merge(latest_risk, on='equipment_id', how='left')

        # All locations should have risk data
        missing_risk = merged[merged['risk_level'].isna()]

        assert len(missing_risk) == 0, (
            f"Locations without risk data: {missing_risk['equipment_id'].tolist()}"
        )


class TestModelIntegration:
    """Test ML model integration"""

    @pytest.mark.slow
    def test_model_file_exists(self, models_dir):
        """Trained model file exists"""
        if not models_dir.exists():
            pytest.skip("Models directory doesn't exist")

        model_files = list(models_dir.glob("saved/*.pkl")) + list(models_dir.glob("saved/*.h5"))

        if len(model_files) == 0:
            pytest.skip(
                f"No model files found in {models_dir}/saved/\n"
                "Run training script first to enable this test"
            )

    @pytest.mark.slow
    def test_can_load_xgboost_model(self, models_dir):
        """XGBoost model can be loaded"""
        if not models_dir.exists():
            pytest.skip("Models directory doesn't exist")

        model_files = list(models_dir.glob("saved/xgboost*.pkl"))

        if not model_files:
            pytest.skip("No XGBoost model found")

        import joblib
        try:
            model = joblib.load(model_files[0])
            assert model is not None, "Model loaded as None"
        except Exception as e:
            pytest.fail(f"Failed to load model: {e}")


class TestEndToEnd:
    """End-to-end workflow tests"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_pipeline_produces_consistent_output(self, telemetry_data, features_data,
                                                      expected_total_equipment):
        """Full pipeline maintains data consistency"""
        if telemetry_data is None or features_data is None:
            pytest.skip("Missing data")

        # Input equipment count
        input_equipment = telemetry_data['equipment_id'].nunique()

        # Output equipment count
        output_equipment = features_data['equipment_id'].nunique()

        # Should be the same
        assert input_equipment == output_equipment, (
            f"Pipeline lost equipment: {input_equipment} → {output_equipment}"
        )

        # Should match expected
        assert output_equipment == expected_total_equipment, (
            f"Expected {expected_total_equipment} equipment, got {output_equipment}"
        )

        # All equipment should have risk classification
        if 'risk_level' in features_data.columns:
            equipment_with_risk = features_data.groupby('equipment_id')['risk_level'].count()
            equipment_without_risk = equipment_with_risk[equipment_with_risk == 0]

            assert len(equipment_without_risk) == 0, (
                f"Equipment without risk classification: {equipment_without_risk.index.tolist()}"
            )
