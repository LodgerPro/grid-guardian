"""
Pytest Configuration and Fixtures for Grid Guardian Tests

This file provides dynamic fixtures that automatically discover and adapt to
the actual project structure, data files, and column names.
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════
# PROJECT STRUCTURE FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def app_dir(project_root):
    """Get app directory"""
    return project_root / "app"


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Get data directory"""
    return project_root / "data"


@pytest.fixture(scope="session")
def src_dir(project_root):
    """Get src directory"""
    return project_root / "src"


@pytest.fixture(scope="session")
def models_dir(project_root):
    """Get models directory"""
    return project_root / "models"


# ═══════════════════════════════════════════════════════════
# FILE DISCOVERY FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def data_files(data_dir):
    """
    Discover all data files dynamically

    Returns:
        dict: {
            'parquet': [Path, ...],
            'csv': [Path, ...]
        }
    """
    if not data_dir.exists():
        return {'parquet': [], 'csv': []}

    return {
        'parquet': list(data_dir.glob("**/*.parquet")),
        'csv': list(data_dir.glob("**/*.csv")),
    }


@pytest.fixture(scope="session")
def app_pages(app_dir):
    """
    Discover all Streamlit page files

    Returns:
        list[Path]: All .py files in app/ and app/pages/
    """
    pages = []

    # Home page
    if (app_dir / "Home.py").exists():
        pages.append(app_dir / "Home.py")

    # Page directory
    pages_dir = app_dir / "pages"
    if pages_dir.exists():
        pages.extend(list(pages_dir.glob("*.py")))

    return sorted(pages)


@pytest.fixture(scope="session")
def src_modules(src_dir):
    """Discover all source modules"""
    if not src_dir.exists():
        return []
    return list(src_dir.glob("*.py"))


# ═══════════════════════════════════════════════════════════
# DATA LOADING FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def telemetry_data(data_files):
    """
    Load actual telemetry data (grid_telemetry_data.parquet)

    Returns:
        pd.DataFrame or None
    """
    parquet_files = [
        f for f in data_files['parquet']
        if 'telemetry' in f.name.lower() or 'grid' in f.name.lower()
    ]

    # Prefer raw data
    for f in parquet_files:
        if 'raw' in str(f):
            try:
                return pd.read_parquet(f)
            except Exception as e:
                print(f"Warning: Could not load {f}: {e}")

    # Fallback to any telemetry file
    for f in parquet_files:
        try:
            return pd.read_parquet(f)
        except Exception:
            continue

    return None


@pytest.fixture(scope="session")
def features_data(data_files):
    """
    Load processed features.csv

    Returns:
        pd.DataFrame or None
    """
    csv_files = [
        f for f in data_files['csv']
        if 'features' in f.name.lower()
    ]

    for f in csv_files:
        try:
            return pd.read_csv(f)
        except Exception:
            continue

    return None


@pytest.fixture(scope="session")
def location_data(data_files):
    """
    Load equipment locations data

    Returns:
        pd.DataFrame or None
    """
    parquet_files = [
        f for f in data_files['parquet']
        if 'location' in f.name.lower() or 'equipment' in f.name.lower()
    ]

    for f in parquet_files:
        try:
            return pd.read_parquet(f)
        except Exception:
            continue

    return None


# ═══════════════════════════════════════════════════════════
# COLUMN & SCHEMA FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def telemetry_columns(telemetry_data):
    """Get actual column names from telemetry data"""
    if telemetry_data is not None:
        return telemetry_data.columns.tolist()
    return []


@pytest.fixture(scope="session")
def features_columns(features_data):
    """Get actual column names from features data"""
    if features_data is not None:
        return features_data.columns.tolist()
    return []


@pytest.fixture(scope="session")
def expected_equipment_ids(telemetry_data):
    """Get list of actual equipment IDs from data"""
    if telemetry_data is not None and 'equipment_id' in telemetry_data.columns:
        return sorted(telemetry_data['equipment_id'].unique())
    return []


# ═══════════════════════════════════════════════════════════
# SAMPLE DATA FIXTURES (for fast tests)
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_telemetry(telemetry_data):
    """
    Get small sample of telemetry data for fast tests

    Returns:
        pd.DataFrame: 1000 random rows
    """
    if telemetry_data is None:
        pytest.skip("No telemetry data available")

    n = min(1000, len(telemetry_data))
    return telemetry_data.sample(n=n, random_state=42)


@pytest.fixture
def sample_features(features_data):
    """
    Get small sample of features data for fast tests

    Returns:
        pd.DataFrame: 1000 random rows with stratified risk_level
    """
    if features_data is None:
        pytest.skip("No features data available")

    if 'risk_level' in features_data.columns:
        # Stratified sample
        n_per_level = min(350, len(features_data) // 3)
        samples = []
        for level in [0, 1, 2]:
            level_data = features_data[features_data['risk_level'] == level]
            if len(level_data) > 0:
                n = min(n_per_level, len(level_data))
                samples.append(level_data.sample(n=n, random_state=42))

        if samples:
            return pd.concat(samples, ignore_index=True).sample(frac=1, random_state=42)

    # Fallback to random sample
    n = min(1000, len(features_data))
    return features_data.sample(n=n, random_state=42)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def expected_substations():
    """Expected number of substations"""
    return 10


@pytest.fixture(scope="session")
def expected_equipment_per_substation():
    """Expected number of equipment units per substation"""
    return 5


@pytest.fixture(scope="session")
def expected_total_equipment(expected_substations, expected_equipment_per_substation):
    """Expected total number of equipment units"""
    return expected_substations * expected_equipment_per_substation


@pytest.fixture(scope="session")
def expected_risk_levels():
    """Expected risk level values"""
    return [0, 1, 2]  # Low, Medium, High


@pytest.fixture(scope="session")
def expected_risk_distribution():
    """
    Expected risk distribution percentages

    Returns:
        dict: {risk_level: percentage}
    """
    return {
        0: 0.75,  # 75% low risk
        1: 0.20,  # 20% medium risk
        2: 0.05   # 5% high risk
    }


# ═══════════════════════════════════════════════════════════
# VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def validate_columns():
    """
    Helper function to validate column presence

    Usage:
        validate_columns(df, ['col1', 'col2'], "Dataset name")
    """
    def _validate(df, required_cols, dataset_name="DataFrame"):
        if df is None:
            pytest.skip(f"{dataset_name} not available")

        missing = set(required_cols) - set(df.columns)
        if missing:
            pytest.fail(
                f"{dataset_name} missing columns: {missing}\n"
                f"Available: {sorted(df.columns)}"
            )
        return True

    return _validate


@pytest.fixture
def check_risk_distribution():
    """
    Helper to validate risk distribution is within tolerance

    Usage:
        check_risk_distribution(df, expected_dist, tolerance=0.05)
    """
    def _check(df, expected_dist, tolerance=0.05):
        if 'risk_level' not in df.columns:
            pytest.skip("No risk_level column")

        actual_dist = df['risk_level'].value_counts(normalize=True).to_dict()

        for level, expected_pct in expected_dist.items():
            actual_pct = actual_dist.get(level, 0)
            diff = abs(actual_pct - expected_pct)

            assert diff <= tolerance, (
                f"Risk level {level}: expected {expected_pct:.1%}, "
                f"got {actual_pct:.1%} (diff: {diff:.1%})"
            )

        return True

    return _check


# ═══════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
