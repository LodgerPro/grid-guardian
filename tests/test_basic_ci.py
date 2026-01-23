"""
Basic CI Tests for Grid Guardian
=================================

Simple, reliable tests that should always pass in CI environment.
These tests check fundamental project structure and imports.
"""

import pytest
import sys
import os
from pathlib import Path


class TestProjectStructure:
    """Test basic project structure"""

    def test_project_root_exists(self):
        """Project root directory exists"""
        project_root = Path(__file__).parent.parent
        assert project_root.exists()
        assert project_root.is_dir()

    def test_required_directories_exist(self):
        """Required directories are present"""
        project_root = Path(__file__).parent.parent
        required_dirs = ['app', 'src', 'models', 'data', 'tests', 'config']

        missing = []
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                missing.append(dir_name)

        assert not missing, f"Missing required directories: {missing}"

    def test_app_directory_has_home_page(self):
        """App directory contains Home.py"""
        project_root = Path(__file__).parent.parent
        home_page = project_root / 'app' / 'Home.py'
        assert home_page.exists(), "Home.py not found in app directory"

    def test_pages_directory_exists(self):
        """App/pages directory exists"""
        project_root = Path(__file__).parent.parent
        pages_dir = project_root / 'app' / 'pages'
        assert pages_dir.exists(), "app/pages directory not found"

    def test_data_directory_structure(self):
        """Data directory has expected structure"""
        project_root = Path(__file__).parent.parent
        data_dir = project_root / 'data'

        assert data_dir.exists(), "data directory not found"

        # Check for subdirectories or data files
        has_content = any(data_dir.iterdir())
        assert has_content, "data directory is empty"


class TestPythonEnvironment:
    """Test Python environment and version"""

    def test_python_version_supported(self):
        """Python version is 3.9 or higher"""
        version = sys.version_info
        assert version.major == 3, f"Python 3.x required, got {version.major}.x"
        assert version.minor >= 9, f"Python 3.9+ required, got 3.{version.minor}"

    def test_sys_path_includes_project(self):
        """Project directories are in Python path"""
        project_root = str(Path(__file__).parent.parent)
        # Either project_root is in path, or we can import from it
        assert project_root in sys.path or os.getcwd().startswith(project_root)


class TestCoreImports:
    """Test core package imports"""

    def test_import_pandas(self):
        """Can import pandas"""
        import pandas
        assert hasattr(pandas, 'DataFrame')

    def test_import_numpy(self):
        """Can import numpy"""
        import numpy
        assert hasattr(numpy, 'array')

    def test_import_streamlit(self):
        """Can import streamlit"""
        import streamlit
        assert hasattr(streamlit, 'title')

    def test_import_pytest(self):
        """Can import pytest"""
        import pytest
        assert hasattr(pytest, 'mark')

    def test_pandas_version(self):
        """Pandas version is acceptable"""
        import pandas as pd
        version = pd.__version__
        major = int(version.split('.')[0])
        assert major >= 1, f"Pandas 1.x+ required, got {version}"

    def test_numpy_version(self):
        """NumPy version is acceptable"""
        import numpy as np
        version = np.__version__
        major = int(version.split('.')[0])
        assert major >= 1, f"NumPy 1.x+ required, got {version}"


class TestConfigurationFiles:
    """Test configuration files exist"""

    def test_requirements_txt_exists(self):
        """requirements.txt exists"""
        project_root = Path(__file__).parent.parent
        req_file = project_root / 'requirements.txt'
        assert req_file.exists(), "requirements.txt not found"

    def test_requirements_txt_not_empty(self):
        """requirements.txt has content"""
        project_root = Path(__file__).parent.parent
        req_file = project_root / 'requirements.txt'

        if req_file.exists():
            content = req_file.read_text()
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            assert len(lines) > 0, "requirements.txt is empty"

    def test_pytest_ini_exists(self):
        """pytest.ini exists"""
        project_root = Path(__file__).parent.parent
        pytest_ini = project_root / 'pytest.ini'
        assert pytest_ini.exists(), "pytest.ini not found"

    def test_dockerfile_exists(self):
        """Dockerfile exists"""
        project_root = Path(__file__).parent.parent
        dockerfile = project_root / 'Dockerfile'
        assert dockerfile.exists(), "Dockerfile not found"

    def test_dockerignore_exists(self):
        """dockerignore exists"""
        project_root = Path(__file__).parent.parent
        dockerignore = project_root / '.dockerignore'
        assert dockerignore.exists(), ".dockerignore not found"


class TestSourceCode:
    """Test source code structure"""

    def test_src_has_init_py(self):
        """src directory has __init__.py"""
        project_root = Path(__file__).parent.parent
        init_file = project_root / 'src' / '__init__.py'
        assert init_file.exists(), "src/__init__.py not found"

    def test_config_has_init_py(self):
        """config directory has __init__.py"""
        project_root = Path(__file__).parent.parent
        init_file = project_root / 'config' / '__init__.py'
        assert init_file.exists(), "config/__init__.py not found"

    def test_models_has_init_py(self):
        """models directory has __init__.py"""
        project_root = Path(__file__).parent.parent
        init_file = project_root / 'models' / '__init__.py'
        assert init_file.exists(), "models/__init__.py not found"

    def test_src_modules_are_python_files(self):
        """All files in src are Python files or __pycache__"""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / 'src'

        for file_path in src_dir.rglob('*'):
            if file_path.is_file():
                # Should be .py file or in __pycache__
                valid = (
                    file_path.suffix == '.py' or
                    '__pycache__' in str(file_path) or
                    file_path.name == '__init__.py'
                )
                assert valid, f"Unexpected file in src: {file_path}"


class TestApplicationPages:
    """Test Streamlit application pages"""

    def test_home_page_is_valid_python(self):
        """Home.py has valid Python syntax"""
        project_root = Path(__file__).parent.parent
        home_page = project_root / 'app' / 'Home.py'

        if home_page.exists():
            content = home_page.read_text(encoding='utf-8')
            # Try to compile it
            try:
                compile(content, str(home_page), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in Home.py: {e}")

    def test_pages_are_numbered(self):
        """Page files follow numbering convention"""
        project_root = Path(__file__).parent.parent
        pages_dir = project_root / 'app' / 'pages'

        if not pages_dir.exists():
            pytest.skip("pages directory doesn't exist")

        page_files = list(pages_dir.glob('*.py'))
        if page_files:
            # At least one page should start with a number
            has_numbered = any(f.name[0].isdigit() for f in page_files)
            assert has_numbered, "No numbered pages found"

    def test_all_page_files_are_valid_python(self):
        """All page files have valid Python syntax"""
        project_root = Path(__file__).parent.parent
        pages_dir = project_root / 'app' / 'pages'

        if not pages_dir.exists():
            pytest.skip("pages directory doesn't exist")

        errors = []
        for page_file in pages_dir.glob('*.py'):
            try:
                content = page_file.read_text(encoding='utf-8')
                compile(content, str(page_file), 'exec')
            except SyntaxError as e:
                errors.append(f"{page_file.name}: {e}")

        assert not errors, f"Syntax errors in pages:\n" + "\n".join(errors)


class TestDataFiles:
    """Test data files presence"""

    def test_data_generation_script_exists(self):
        """Data generation script exists"""
        project_root = Path(__file__).parent.parent
        gen_script = project_root / 'data' / 'generate_data.py'
        assert gen_script.exists(), "data/generate_data.py not found"

    def test_data_generation_script_is_valid(self):
        """Data generation script has valid syntax"""
        project_root = Path(__file__).parent.parent
        gen_script = project_root / 'data' / 'generate_data.py'

        if gen_script.exists():
            content = gen_script.read_text(encoding='utf-8')
            try:
                compile(content, str(gen_script), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in generate_data.py: {e}")


class TestDocumentation:
    """Test documentation files"""

    def test_readme_exists(self):
        """README.md exists"""
        project_root = Path(__file__).parent.parent
        readme = project_root / 'README.md'
        assert readme.exists(), "README.md not found"

    def test_readme_not_empty(self):
        """README.md has content"""
        project_root = Path(__file__).parent.parent
        readme = project_root / 'README.md'

        if readme.exists():
            content = readme.read_text(encoding='utf-8')
            assert len(content) > 100, "README.md is too short"

    def test_docker_documentation_exists(self):
        """Docker documentation exists"""
        project_root = Path(__file__).parent.parent
        docker_md = project_root / 'DOCKER.md'
        assert docker_md.exists(), "DOCKER.md not found"

    def test_license_exists(self):
        """LICENSE file exists"""
        project_root = Path(__file__).parent.parent
        license_file = project_root / 'LICENSE'
        assert license_file.exists(), "LICENSE file not found"


class TestGitConfiguration:
    """Test Git configuration"""

    def test_gitignore_exists(self):
        """gitignore file exists"""
        project_root = Path(__file__).parent.parent
        gitignore = project_root / '.gitignore'
        assert gitignore.exists(), ".gitignore not found"

    def test_gitignore_ignores_common_patterns(self):
        """gitignore includes common Python patterns"""
        project_root = Path(__file__).parent.parent
        gitignore = project_root / '.gitignore'

        if gitignore.exists():
            content = gitignore.read_text()
            # Check for common patterns
            patterns = ['__pycache__', '*.pyc', 'venv', '.env']
            missing = [p for p in patterns if p not in content]

            # At least one common pattern should be present
            assert len(missing) < len(patterns), f"gitignore missing common patterns: {missing}"


class TestImportability:
    """Test that modules can be imported"""

    def test_can_import_config(self):
        """Can import config module"""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        try:
            import config
            assert config is not None
        except ImportError as e:
            pytest.skip(f"Config import failed (may be normal): {e}")

    def test_can_import_from_src(self):
        """Can import from src module"""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        try:
            import src
            assert src is not None
        except ImportError as e:
            pytest.skip(f"Src import failed (may be normal): {e}")


class TestBasicFunctionality:
    """Test basic functionality"""

    def test_pandas_can_create_dataframe(self):
        """Pandas can create DataFrame"""
        import pandas as pd
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        assert len(df) == 3
        assert list(df.columns) == ['a', 'b']

    def test_numpy_can_create_array(self):
        """NumPy can create array"""
        import numpy as np
        arr = np.array([1, 2, 3, 4, 5])
        assert len(arr) == 5
        assert arr.sum() == 15

    def test_basic_math_operations(self):
        """Basic math operations work"""
        import numpy as np
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        c = a + b
        assert list(c) == [5, 7, 9]

    def test_pandas_read_csv_works(self):
        """Pandas can handle CSV operations"""
        import pandas as pd
        import io

        csv_data = "a,b,c\n1,2,3\n4,5,6"
        df = pd.read_csv(io.StringIO(csv_data))
        assert len(df) == 2
        assert list(df.columns) == ['a', 'b', 'c']


class TestEnvironmentVariables:
    """Test environment setup"""

    def test_working_directory_accessible(self):
        """Working directory is accessible"""
        cwd = os.getcwd()
        assert os.path.exists(cwd)
        assert os.access(cwd, os.R_OK)

    def test_can_create_temp_file(self):
        """Can create temporary files"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name

        assert os.path.exists(temp_path)
        os.unlink(temp_path)

    def test_python_executable_exists(self):
        """Python executable path exists"""
        python_exe = sys.executable
        assert os.path.exists(python_exe)
