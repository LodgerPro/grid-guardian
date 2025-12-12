"""
Tests for ML model files and structure
"""
import pytest
from pathlib import Path
import pickle


class TestModelValidation:
    """Test ML models structure and availability"""

    def test_models_directory_exists(self, models_dir):
        """Verify models directory exists"""
        assert models_dir.exists(), "models/ directory not found"
        assert models_dir.is_dir(), "models/ is not a directory"

    def test_training_scripts_exist(self, models_dir):
        """Verify training scripts are present"""
        expected_scripts = [
            "train_xgboost.py",
            "train_lstm.py"
        ]

        for script in expected_scripts:
            script_path = models_dir / script
            assert script_path.exists(), f"Training script {script} not found"

    def test_saved_models_directory(self, models_dir):
        """Check for saved models directory"""
        saved_dir = models_dir / "saved"

        if saved_dir.exists():
            # If directory exists, check for model files
            model_files = list(saved_dir.glob("*.pkl")) + list(saved_dir.glob("*.h5"))
            print(f"\nFound {len(model_files)} saved models in models/saved/")
        else:
            pytest.skip("models/saved/ directory not created yet (models not trained)")

    def test_model_file_structure(self, models_dir):
        """Verify model files have correct structure"""
        saved_dir = models_dir / "saved"

        if not saved_dir.exists():
            pytest.skip("No saved models to validate")

        pkl_files = list(saved_dir.glob("*.pkl"))

        for pkl_file in pkl_files:
            try:
                with open(pkl_file, 'rb') as f:
                    model = pickle.load(f)
                print(f"\n✓ Successfully loaded {pkl_file.name}")
            except Exception as e:
                pytest.fail(f"Failed to load {pkl_file.name}: {e}")

    def test_xgboost_script_syntax(self, models_dir):
        """Verify XGBoost training script is valid Python"""
        script = models_dir / "train_xgboost.py"

        try:
            with open(script, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, script.name, 'exec')
        except SyntaxError as e:
            pytest.fail(f"XGBoost script has syntax error: {e}")

    def test_lstm_script_syntax(self, models_dir):
        """Verify LSTM training script is valid Python"""
        script = models_dir / "train_lstm.py"

        try:
            with open(script, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, script.name, 'exec')
        except SyntaxError as e:
            pytest.fail(f"LSTM script has syntax error: {e}")

    def test_xgboost_imports(self, models_dir):
        """Verify XGBoost script imports required packages"""
        script = models_dir / "train_xgboost.py"
        content = script.read_text(encoding='utf-8')

        required_imports = ['xgboost', 'pandas', 'sklearn']

        for import_name in required_imports:
            assert import_name in content, (
                f"XGBoost script missing import: {import_name}"
            )

    def test_lstm_imports(self, models_dir):
        """Verify LSTM script imports required packages"""
        script = models_dir / "train_lstm.py"
        content = script.read_text(encoding='utf-8')

        required_imports = ['tensorflow', 'pandas', 'numpy']

        for import_name in required_imports:
            assert import_name in content, (
                f"LSTM script missing import: {import_name}"
            )
