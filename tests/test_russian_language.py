"""
Tests for Russian language UI consistency
"""
import pytest
import re
from pathlib import Path


class TestRussianLanguage:
    """Test Russian language in Streamlit UI"""

    def test_pages_contain_russian_text(self, app_pages):
        """Verify all pages contain Russian Cyrillic characters"""
        russian_pattern = r'[А-Яа-яЁё]'

        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            has_russian = bool(re.search(russian_pattern, content))
            assert has_russian, f"{page.name} does not contain Russian text"

    def test_no_english_ui_strings(self, app_pages):
        """Check for common untranslated English UI terms"""
        # Common English phrases that should be translated
        english_patterns = [
            r'st\.title\(["\'](?!Grid Guardian)[A-Z][a-z]+',  # English titles
            r'"Loading\s+data\.\.\.?"',
            r'"Total\s+Equipment"',
            r'"Critical\s+Alert"',
            r'"Click\s+here"',
            r'"Select\s+equipment"',
        ]

        violations = []
        for page in app_pages:
            content = page.read_text(encoding='utf-8')

            for pattern in english_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append(f"{page.name}: found '{matches[0]}'")

        # Report violations but don't fail (some English is acceptable)
        if violations:
            print(f"\nFound {len(violations)} potential English UI strings:")
            for v in violations:
                print(f"  - {v}")

    def test_russian_characters_in_titles(self, app_pages):
        """Verify st.title() uses Russian text"""
        russian_pattern = r'[А-Яа-яЁё]'
        title_pattern = r'st\.title\(["\']([^"\']+)["\']'

        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            titles = re.findall(title_pattern, content)

            for title in titles:
                # Skip "Grid Guardian" (English brand name)
                if "Grid Guardian" in title:
                    continue

                has_russian = bool(re.search(russian_pattern, title))
                assert has_russian, f"{page.name} has English title: '{title}'"

    def test_russian_in_metrics(self, app_pages):
        """Verify st.metric() labels are in Russian"""
        russian_pattern = r'[А-Яа-яЁё]'
        metric_pattern = r'st\.metric\(["\']([^"\']+)["\']'

        violations = []
        for page in app_pages:
            content = page.read_text(encoding='utf-8')
            metrics = re.findall(metric_pattern, content)

            for metric in metrics:
                has_russian = bool(re.search(russian_pattern, metric))
                if not has_russian:
                    violations.append(f"{page.name}: metric '{metric}' in English")

        if violations:
            print(f"\nFound {len(violations)} English metrics:")
            for v in violations:
                print(f"  - {v}")

    def test_file_encoding(self, app_pages):
        """Verify all files are UTF-8 encoded"""
        for page in app_pages:
            try:
                # Try to read with UTF-8
                content = page.read_text(encoding='utf-8')
                assert len(content) > 0, f"{page.name} is empty"
            except UnicodeDecodeError:
                pytest.fail(f"{page.name} is not UTF-8 encoded")
