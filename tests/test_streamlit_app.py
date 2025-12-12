"""
Streamlit Application Tests for Grid Guardian

Tests the Streamlit dashboard pages:
- Page existence and syntax
- Import availability
- Function presence
- Russian language consistency
"""

import pytest
import ast
import re
import importlib.util
from pathlib import Path


class TestPageFiles:
    """Test Streamlit page files exist and are valid"""

    def test_all_discovered_pages_exist(self, app_pages):
        """All discovered page files exist"""
        assert len(app_pages) > 0, "No app pages found"

        for page in app_pages:
            assert page.exists(), f"Page file not found: {page}"
            assert page.suffix == '.py', f"Page is not a Python file: {page}"

    def test_home_page_exists(self, app_dir):
        """Home.py exists"""
        home = app_dir / "Home.py"
        assert home.exists(), f"Home.py not found at {home}"

    def test_expected_pages_exist(self, app_dir):
        """Expected page files exist"""
        pages_dir = app_dir / "pages"
        if not pages_dir.exists():
            pytest.skip("Pages directory doesn't exist")

        # Expected pages (by number prefix)
        expected_patterns = [
            r"1.*Monitoring\.py",
            r"2.*Predictions\.py",
            r"3.*Financial\.py",
            r"4.*Maps\.py"
        ]

        page_files = [f.name for f in pages_dir.glob("*.py")]

        for pattern in expected_patterns:
            matches = [f for f in page_files if re.match(pattern, f)]
            assert matches, (
                f"No page matching pattern '{pattern}'\n"
                f"Available pages: {page_files}"
            )


class TestPageSyntax:
    """Test pages are valid Python files"""

    def test_pages_are_valid_python(self, app_pages):
        """All pages have valid Python syntax"""
        errors = []

        for page in app_pages:
            try:
                with open(page, 'r', encoding='utf-8') as f:
                    content = f.read()
                    ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{page.name}: Line {e.lineno}: {e.msg}")
            except Exception as e:
                errors.append(f"{page.name}: {str(e)}")

        assert not errors, "Syntax errors found:\n" + "\n".join(errors)

    def test_pages_have_imports(self, app_pages):
        """All pages have import statements"""
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            has_import = 'import ' in content
            assert has_import, f"{page.name} has no import statements"

    def test_pages_import_streamlit(self, app_pages):
        """All pages import streamlit"""
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            has_st_import = re.search(r'import\s+streamlit', content)
            assert has_st_import, f"{page.name} doesn't import streamlit"


class TestRequiredDependencies:
    """Test required packages are installed"""

    def test_core_packages_available(self):
        """Core packages can be imported"""
        required = [
            'streamlit',
            'pandas',
            'numpy',
            'plotly',
        ]

        missing = []
        for module_name in required:
            try:
                __import__(module_name)
            except ImportError:
                missing.append(module_name)

        assert not missing, f"Required modules not installed: {missing}"

    def test_ml_packages_available(self):
        """ML packages can be imported"""
        ml_packages = [
            'sklearn',
            'xgboost',
        ]

        missing = []
        for module_name in ml_packages:
            try:
                __import__(module_name)
            except ImportError:
                missing.append(module_name)

        assert not missing, f"ML modules not installed: {missing}"

    def test_data_packages_available(self):
        """Data handling packages can be imported"""
        data_packages = [
            'pyarrow',
        ]

        missing = []
        for module_name in data_packages:
            try:
                __import__(module_name)
            except ImportError:
                missing.append(module_name)

        assert not missing, f"Data modules not installed: {missing}"


class TestHomePage:
    """Test Home.py specific functionality"""

    def test_home_has_load_data_function(self, app_dir):
        """Home.py has load_sample_data function"""
        home = app_dir / "Home.py"
        content = home.read_text(encoding='utf-8')

        has_load_func = re.search(r'def\s+load_sample_data', content)
        assert has_load_func, "Home.py missing load_sample_data() function"

    def test_home_has_caching(self, app_dir):
        """Home.py uses Streamlit caching"""
        home = app_dir / "Home.py"
        content = home.read_text(encoding='utf-8')

        has_cache = '@st.cache_data' in content or '@st.cache_resource' in content
        assert has_cache, "Home.py doesn't use Streamlit caching"

    def test_home_has_risk_overview(self, app_dir):
        """Home.py has risk overview function"""
        home = app_dir / "Home.py"
        content = home.read_text(encoding='utf-8')

        has_risk = re.search(r'def\s+display_risk_overview', content)
        assert has_risk, "Home.py missing display_risk_overview() function"


class TestPredictionsPage:
    """Test Predictions page specific functionality"""

    def test_predictions_page_exists(self, app_pages):
        """Predictions page exists"""
        pred_pages = [p for p in app_pages if 'Prediction' in p.name or '🔮' in p.name]
        assert pred_pages, f"No Predictions page found in {[p.name for p in app_pages]}"

    def test_predictions_has_load_model_function(self, app_pages):
        """Predictions page has load_model function"""
        pred_pages = [p for p in app_pages if 'Prediction' in p.name or '🔮' in p.name]
        if not pred_pages:
            pytest.skip("No Predictions page")

        content = pred_pages[0].read_text(encoding='utf-8')
        has_load_model = re.search(r'def\s+load_model', content)
        assert has_load_model, "Predictions page missing load_model() function"

    def test_predictions_uses_risk_level(self, app_pages):
        """Predictions page uses risk_level for classification"""
        pred_pages = [p for p in app_pages if 'Prediction' in p.name or '🔮' in p.name]
        if not pred_pages:
            pytest.skip("No Predictions page")

        content = pred_pages[0].read_text(encoding='utf-8')
        uses_risk_level = 'risk_level' in content
        assert uses_risk_level, "Predictions page doesn't use risk_level"


class TestMapsPage:
    """Test Maps page specific functionality"""

    def test_maps_page_exists(self, app_pages):
        """Maps page exists"""
        map_pages = [p for p in app_pages if 'Map' in p.name or '🗺' in p.name]
        assert map_pages, f"No Maps page found in {[p.name for p in app_pages]}"

    def test_maps_imports_folium(self, app_pages):
        """Maps page imports folium"""
        map_pages = [p for p in app_pages if 'Map' in p.name or '🗺' in p.name]
        if not map_pages:
            pytest.skip("No Maps page")

        content = map_pages[0].read_text(encoding='utf-8')
        has_folium = re.search(r'import\s+folium', content)
        assert has_folium, "Maps page doesn't import folium"

    def test_maps_has_load_location_function(self, app_pages):
        """Maps page has load_location_data function"""
        map_pages = [p for p in app_pages if 'Map' in p.name or '🗺' in p.name]
        if not map_pages:
            pytest.skip("No Maps page")

        content = map_pages[0].read_text(encoding='utf-8')
        has_load_loc = re.search(r'def\s+load_location', content)
        assert has_load_loc, "Maps page missing load_location_data() function"


class TestPageStructure:
    """Test common page structure"""

    def test_pages_have_page_config(self, app_pages):
        """Pages set page config"""
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            has_config = 'set_page_config' in content
            # Home page might not have it, but pages should
            if 'pages' in str(page):
                assert has_config, f"{page.name} doesn't set page config"

    def test_pages_have_title(self, app_pages):
        """Pages have a title"""
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            has_title = 'st.title' in content
            assert has_title, f"{page.name} doesn't have st.title()"

    def test_pages_use_markdown_separators(self, app_pages):
        """Pages use markdown for section separation"""
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            # At least some pages should use ---
            has_separator = '---' in content or 'st.markdown("---")' in content
            # This is optional, so just log if missing
            if not has_separator:
                print(f"Note: {page.name} doesn't use markdown separators")


class TestRussianLanguage:
    """Test Russian language consistency in UI"""

    def test_pages_contain_russian_text(self, app_pages):
        """Pages contain Russian (Cyrillic) characters"""
        russian_pattern = r'[А-Яа-яЁё]'

        missing_russian = []
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            has_russian = bool(re.search(russian_pattern, content))
            if not has_russian:
                missing_russian.append(page.name)

        assert not missing_russian, (
            f"Pages without Russian text: {missing_russian}\n"
            "All UI should be in Russian"
        )

    def test_no_common_english_ui_terms(self, app_pages):
        """Check for common untranslated English UI terms"""
        # Common UI terms that should be translated
        english_terms = [
            (r'\bLoading\b', 'Should be "Загрузка"'),
            (r'\bError\b', 'Should be "Ошибка"'),
            (r'\bWarning\b', 'Should be "Предупреждение"'),
            (r'\bSuccess\b', 'Should be "Успех"'),
        ]

        violations = []
        for page in app_pages:
            content = page.read_text(encoding='utf-8')

            for pattern, suggestion in english_terms:
                # Skip comments and imports
                lines = [line for line in content.split('\n')
                        if not line.strip().startswith('#') and 'import' not in line]
                content_no_comments = '\n'.join(lines)

                if re.search(pattern, content_no_comments):
                    violations.append(f"{page.name}: Found '{pattern}' - {suggestion}")

        # This is a warning, not a failure (some English terms might be in variable names)
        if violations:
            pytest.warns(UserWarning, match="English UI terms found")
            print("Warning: Possible English UI terms:\n" + "\n".join(violations))

    def test_streamlit_calls_use_russian(self, app_pages):
        """Streamlit UI calls use Russian text"""
        # Extract st.title, st.header, st.subheader calls
        ui_patterns = [
            r'st\.title\(["\']([^"\']+)["\']',
            r'st\.header\(["\']([^"\']+)["\']',
            r'st\.subheader\(["\']([^"\']+)["\']',
        ]

        russian_pattern = r'[А-Яа-яЁё]'
        violations = []

        for page in app_pages:
            content = page.read_text(encoding='utf-8')

            for pattern in ui_patterns:
                matches = re.findall(pattern, content)
                for text in matches:
                    if not re.search(russian_pattern, text):
                        # Ignore "Grid Guardian" and emoji
                        if text not in ['Grid Guardian'] and not text.startswith('�'):
                            violations.append(f"{page.name}: '{text}' not in Russian")

        assert not violations, (
            "UI text not in Russian:\n" + "\n".join(violations[:10])  # Show first 10
        )


class TestFileEncoding:
    """Test file encoding is UTF-8"""

    def test_pages_are_utf8_encoded(self, app_pages):
        """All pages are UTF-8 encoded"""
        encoding_errors = []

        for page in app_pages:
            try:
                page.read_text(encoding='utf-8')
            except UnicodeDecodeError as e:
                encoding_errors.append(f"{page.name}: {str(e)}")

        assert not encoding_errors, (
            "UTF-8 encoding errors:\n" + "\n".join(encoding_errors)
        )
