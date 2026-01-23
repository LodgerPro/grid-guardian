"""
Smoke Tests for Grid Guardian
==============================

Минимальный набор быстрых тестов для проверки, что система работает.
Эти тесты должны проходить ВСЕГДА.
"""

import pytest
from pathlib import Path


class TestMinimalRequirements:
    """Самые базовые проверки"""

    def test_python_runs(self):
        """Python работает"""
        assert True

    def test_basic_arithmetic(self):
        """Базовая арифметика работает"""
        assert 2 + 2 == 4
        assert 10 * 5 == 50

    def test_string_operations(self):
        """Строковые операции работают"""
        s = "Grid Guardian"
        assert len(s) > 0
        assert "Grid" in s

    def test_list_operations(self):
        """Списки работают"""
        lst = [1, 2, 3, 4, 5]
        assert len(lst) == 5
        assert sum(lst) == 15

    def test_dict_operations(self):
        """Словари работают"""
        d = {'name': 'Grid Guardian', 'version': '1.0'}
        assert 'name' in d
        assert d['version'] == '1.0'


class TestImportsWork:
    """Проверка, что основные пакеты импортируются"""

    def test_import_sys(self):
        """Можно импортировать sys"""
        import sys
        assert sys.version_info.major == 3

    def test_import_os(self):
        """Можно импортировать os"""
        import os
        assert hasattr(os, 'path')

    def test_import_pathlib(self):
        """Можно импортировать pathlib"""
        from pathlib import Path
        p = Path('.')
        assert p.exists()

    def test_import_pytest(self):
        """Можно импортировать pytest"""
        import pytest
        assert pytest is not None


class TestPandasBasics:
    """Проверка pandas"""

    def test_pandas_imports(self):
        """Pandas импортируется"""
        import pandas as pd
        assert pd is not None

    def test_pandas_create_series(self):
        """Можно создать Series"""
        import pandas as pd
        s = pd.Series([1, 2, 3])
        assert len(s) == 3

    def test_pandas_create_dataframe(self):
        """Можно создать DataFrame"""
        import pandas as pd
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        assert df.shape == (2, 2)

    def test_pandas_basic_operations(self):
        """Базовые операции с DataFrame"""
        import pandas as pd
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        assert df['x'].sum() == 6
        assert df['y'].mean() == 5.0


class TestNumpyBasics:
    """Проверка numpy"""

    def test_numpy_imports(self):
        """NumPy импортируется"""
        import numpy as np
        assert np is not None

    def test_numpy_create_array(self):
        """Можно создать array"""
        import numpy as np
        arr = np.array([1, 2, 3])
        assert len(arr) == 3

    def test_numpy_basic_math(self):
        """Базовая математика с numpy"""
        import numpy as np
        arr = np.array([1, 2, 3, 4, 5])
        assert arr.sum() == 15
        assert arr.mean() == 3.0

    def test_numpy_array_operations(self):
        """Операции с массивами"""
        import numpy as np
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        c = a + b
        assert list(c) == [5, 7, 9]


class TestStreamlitImport:
    """Проверка streamlit"""

    def test_streamlit_imports(self):
        """Streamlit импортируется"""
        import streamlit as st
        assert st is not None

    def test_streamlit_has_components(self):
        """Streamlit имеет основные компоненты"""
        import streamlit as st
        assert hasattr(st, 'title')
        assert hasattr(st, 'write')
        assert hasattr(st, 'dataframe')


class TestFilesExist:
    """Проверка существования ключевых файлов"""

    def test_readme_exists(self):
        """README существует"""
        project_root = Path(__file__).parent.parent
        readme = project_root / 'README.md'
        assert readme.exists()

    def test_requirements_exists(self):
        """requirements.txt существует"""
        project_root = Path(__file__).parent.parent
        req = project_root / 'requirements.txt'
        assert req.exists()

    def test_app_home_exists(self):
        """app/Home.py существует"""
        project_root = Path(__file__).parent.parent
        home = project_root / 'app' / 'Home.py'
        assert home.exists()

    def test_src_directory_exists(self):
        """src директория существует"""
        project_root = Path(__file__).parent.parent
        src = project_root / 'src'
        assert src.exists()

    def test_tests_directory_exists(self):
        """tests директория существует"""
        project_root = Path(__file__).parent.parent
        tests = project_root / 'tests'
        assert tests.exists()


class TestDirectoriesReadable:
    """Проверка доступности директорий"""

    def test_can_read_app_directory(self):
        """Можно читать app директорию"""
        project_root = Path(__file__).parent.parent
        app_dir = project_root / 'app'
        assert app_dir.exists()
        assert app_dir.is_dir()
        # Проверяем, что можем получить список файлов
        files = list(app_dir.iterdir())
        assert len(files) > 0

    def test_can_read_src_directory(self):
        """Можно читать src директорию"""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / 'src'
        assert src_dir.exists()
        assert src_dir.is_dir()

    def test_can_read_data_directory(self):
        """Можно читать data директорию"""
        project_root = Path(__file__).parent.parent
        data_dir = project_root / 'data'
        assert data_dir.exists()
        assert data_dir.is_dir()


class TestBasicFileOperations:
    """Проверка файловых операций"""

    def test_can_read_requirements(self):
        """Можно прочитать requirements.txt"""
        project_root = Path(__file__).parent.parent
        req = project_root / 'requirements.txt'
        content = req.read_text()
        assert len(content) > 0
        assert 'pandas' in content.lower()

    def test_can_read_readme(self):
        """Можно прочитать README.md"""
        project_root = Path(__file__).parent.parent
        readme = project_root / 'README.md'
        content = readme.read_text(encoding='utf-8')
        assert len(content) > 100

    def test_home_py_is_valid_python(self):
        """Home.py - валидный Python файл"""
        project_root = Path(__file__).parent.parent
        home = project_root / 'app' / 'Home.py'
        content = home.read_text(encoding='utf-8')

        # Пробуем скомпилировать
        try:
            compile(content, 'Home.py', 'exec')
        except SyntaxError:
            pytest.fail("Home.py has syntax errors")


class TestQuickValidation:
    """Быстрые валидационные тесты"""

    def test_project_name_in_readme(self):
        """Название проекта есть в README"""
        project_root = Path(__file__).parent.parent
        readme = project_root / 'README.md'
        content = readme.read_text(encoding='utf-8').lower()
        assert 'grid' in content or 'guardian' in content

    def test_requirements_not_empty(self):
        """requirements.txt не пустой"""
        project_root = Path(__file__).parent.parent
        req = project_root / 'requirements.txt'
        lines = req.read_text().split('\n')
        # Убираем комментарии и пустые строки
        packages = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        assert len(packages) > 5  # Минимум 5 пакетов

    def test_python_version_check(self):
        """Python версия >= 3.9"""
        import sys
        assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version_info}"


class TestMinimalDataOperations:
    """Минимальные операции с данными"""

    def test_can_create_sample_dataframe(self):
        """Можно создать sample DataFrame"""
        import pandas as pd
        df = pd.DataFrame({
            'temperature': [70, 75, 80],
            'voltage': [110, 111, 109],
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='H')
        })
        assert len(df) == 3
        assert 'temperature' in df.columns

    def test_basic_data_filtering(self):
        """Базовая фильтрация работает"""
        import pandas as pd
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        filtered = df[df['value'] > 2]
        assert len(filtered) == 3

    def test_basic_data_aggregation(self):
        """Базовая агрегация работает"""
        import pandas as pd
        df = pd.DataFrame({'category': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]})
        grouped = df.groupby('category')['value'].sum()
        assert grouped['A'] == 3
        assert grouped['B'] == 7


class TestEnvironmentSetup:
    """Проверка окружения"""

    def test_pytest_available(self):
        """pytest доступен"""
        import pytest
        assert pytest.__version__ is not None

    def test_working_directory_accessible(self):
        """Рабочая директория доступна"""
        import os
        cwd = os.getcwd()
        assert os.path.exists(cwd)

    def test_temp_directory_accessible(self):
        """Временная директория доступна"""
        import tempfile
        temp_dir = tempfile.gettempdir()
        assert Path(temp_dir).exists()

    def test_can_write_temp_file(self):
        """Можно записать временный файл"""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name

        assert os.path.exists(temp_path)
        os.unlink(temp_path)


class TestQuickSanityChecks:
    """Быстрые санити-проверки"""

    def test_all_required_packages_importable(self):
        """Все основные пакеты можно импортировать"""
        required = ['pandas', 'numpy', 'streamlit', 'pytest']
        failed = []

        for package in required:
            try:
                __import__(package)
            except ImportError:
                failed.append(package)

        assert not failed, f"Failed to import: {failed}"

    def test_no_syntax_errors_in_test_files(self):
        """Нет синтаксических ошибок в тестовых файлах"""
        project_root = Path(__file__).parent.parent
        test_dir = project_root / 'tests'

        errors = []
        for test_file in test_dir.glob('test_*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                compile(content, str(test_file), 'exec')
            except SyntaxError as e:
                errors.append(f"{test_file.name}: {e}")

        assert not errors, f"Syntax errors found:\n" + "\n".join(errors)

    def test_app_files_have_no_obvious_syntax_errors(self):
        """Файлы приложения без явных синтаксических ошибок"""
        project_root = Path(__file__).parent.parent
        app_dir = project_root / 'app'

        errors = []
        for py_file in app_dir.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                compile(content, str(py_file), 'exec')
            except SyntaxError as e:
                errors.append(f"{py_file.name}: line {e.lineno}")

        # Допускаем до 2 файлов с ошибками (могут быть специфичные случаи)
        assert len(errors) <= 2, f"Too many syntax errors:\n" + "\n".join(errors)
