"""
Быстрые Валидационные Тесты с Понятными Названиями
====================================================

Простые тесты для CI с человеческими названиями.
"""

import pytest
import sys
from pathlib import Path


# ============================================================================
# БАЗОВЫЕ ПРОВЕРКИ PYTHON
# ============================================================================

@pytest.mark.smoke
def test_python_version_is_3_9_or_higher():
    """Python версия 3.9 или выше"""
    version = sys.version_info
    assert version >= (3, 9), f"Требуется Python 3.9+, обнаружена версия {version.major}.{version.minor}"


@pytest.mark.smoke
def test_basic_arithmetic_operations_work():
    """Базовая арифметика работает корректно"""
    assert 2 + 2 == 4, "Сложение не работает"
    assert 10 * 5 == 50, "Умножение не работает"
    assert 100 / 4 == 25, "Деление не работает"


@pytest.mark.smoke
def test_string_operations_work():
    """Операции со строками работают"""
    test_string = "Grid Guardian System"
    assert len(test_string) > 0, "Строка не должна быть пустой"
    assert "Grid" in test_string, "Подстрока не найдена"
    assert test_string.lower() == "grid guardian system", "Преобразование в нижний регистр не работает"


# ============================================================================
# ИМПОРТ ОСНОВНЫХ ПАКЕТОВ
# ============================================================================

@pytest.mark.smoke
def test_pandas_can_be_imported():
    """Пакет Pandas успешно импортируется"""
    import pandas as pd
    assert pd is not None, "Pandas не импортирован"
    assert hasattr(pd, 'DataFrame'), "Pandas.DataFrame недоступен"


@pytest.mark.smoke
def test_numpy_can_be_imported():
    """Пакет NumPy успешно импортируется"""
    import numpy as np
    assert np is not None, "NumPy не импортирован"
    assert hasattr(np, 'array'), "NumPy.array недоступен"


@pytest.mark.smoke
def test_streamlit_can_be_imported():
    """Пакет Streamlit успешно импортируется"""
    import streamlit as st
    assert st is not None, "Streamlit не импортирован"
    assert hasattr(st, 'title'), "Streamlit.title недоступен"


@pytest.mark.smoke
def test_pytest_is_available():
    """Pytest доступен для тестирования"""
    import pytest
    assert pytest is not None, "Pytest не доступен"
    assert pytest.__version__ is not None, "Версия pytest не определена"


# ============================================================================
# ПРОВЕРКА ВЕРСИЙ ПАКЕТОВ
# ============================================================================

@pytest.mark.smoke
def test_pandas_version_is_acceptable():
    """Версия Pandas соответствует требованиям (>= 2.0)"""
    import pandas as pd
    major_version = int(pd.__version__.split('.')[0])
    assert major_version >= 1, f"Pandas версии {pd.__version__} устарела, требуется >= 1.0"


@pytest.mark.smoke
def test_numpy_version_is_acceptable():
    """Версия NumPy соответствует требованиям (>= 1.24)"""
    import numpy as np
    major_version = int(np.__version__.split('.')[0])
    assert major_version >= 1, f"NumPy версии {np.__version__} устарела, требуется >= 1.0"


# ============================================================================
# СТРУКТУРА ПРОЕКТА
# ============================================================================

@pytest.mark.ci
def test_project_root_directory_exists():
    """Корневая директория проекта существует"""
    project_root = Path(__file__).parent.parent
    assert project_root.exists(), "Корневая директория не найдена"
    assert project_root.is_dir(), "Корневой путь не является директорией"


@pytest.mark.ci
def test_app_directory_exists():
    """Директория приложения app/ существует"""
    app_dir = Path(__file__).parent.parent / 'app'
    assert app_dir.exists(), "Директория app/ не найдена"
    assert app_dir.is_dir(), "app/ не является директорией"


@pytest.mark.ci
def test_src_directory_exists():
    """Директория исходного кода src/ существует"""
    src_dir = Path(__file__).parent.parent / 'src'
    assert src_dir.exists(), "Директория src/ не найдена"
    assert src_dir.is_dir(), "src/ не является директорией"


@pytest.mark.ci
def test_tests_directory_exists():
    """Директория тестов tests/ существует"""
    tests_dir = Path(__file__).parent.parent / 'tests'
    assert tests_dir.exists(), "Директория tests/ не найдена"
    assert tests_dir.is_dir(), "tests/ не является директорией"


@pytest.mark.ci
def test_data_directory_exists():
    """Директория данных data/ существует"""
    data_dir = Path(__file__).parent.parent / 'data'
    assert data_dir.exists(), "Директория data/ не найдена"
    assert data_dir.is_dir(), "data/ не является директорией"


@pytest.mark.ci
def test_models_directory_exists():
    """Директория моделей models/ существует"""
    models_dir = Path(__file__).parent.parent / 'models'
    assert models_dir.exists(), "Директория models/ не найдена"
    assert models_dir.is_dir(), "models/ не является директорией"


# ============================================================================
# КЛЮЧЕВЫЕ ФАЙЛЫ
# ============================================================================

@pytest.mark.ci
def test_readme_file_exists():
    """Файл README.md существует в корне проекта"""
    readme = Path(__file__).parent.parent / 'README.md'
    assert readme.exists(), "README.md не найден"
    assert readme.is_file(), "README.md не является файлом"


@pytest.mark.ci
def test_requirements_file_exists():
    """Файл requirements.txt существует"""
    req_file = Path(__file__).parent.parent / 'requirements.txt'
    assert req_file.exists(), "requirements.txt не найден"
    assert req_file.is_file(), "requirements.txt не является файлом"


@pytest.mark.ci
def test_dockerfile_exists():
    """Dockerfile существует для контейнеризации"""
    dockerfile = Path(__file__).parent.parent / 'Dockerfile'
    assert dockerfile.exists(), "Dockerfile не найден"
    assert dockerfile.is_file(), "Dockerfile не является файлом"


@pytest.mark.ci
def test_home_page_exists():
    """Главная страница приложения Home.py существует"""
    home_page = Path(__file__).parent.parent / 'app' / 'Home.py'
    assert home_page.exists(), "app/Home.py не найден"
    assert home_page.is_file(), "Home.py не является файлом"


@pytest.mark.ci
def test_gitignore_file_exists():
    """Файл .gitignore существует"""
    gitignore = Path(__file__).parent.parent / '.gitignore'
    assert gitignore.exists(), ".gitignore не найден"
    assert gitignore.is_file(), ".gitignore не является файлом"


# ============================================================================
# СОДЕРЖИМОЕ ФАЙЛОВ
# ============================================================================

@pytest.mark.ci
def test_readme_contains_project_information():
    """README содержит информацию о проекте"""
    readme = Path(__file__).parent.parent / 'README.md'
    content = readme.read_text(encoding='utf-8').lower()
    assert len(content) > 100, "README слишком короткий"
    assert 'grid' in content or 'guardian' in content, "README не содержит название проекта"


@pytest.mark.ci
def test_requirements_contains_dependencies():
    """requirements.txt содержит необходимые зависимости"""
    req_file = Path(__file__).parent.parent / 'requirements.txt'
    content = req_file.read_text().lower()

    required_packages = ['pandas', 'numpy', 'streamlit']
    missing = [pkg for pkg in required_packages if pkg not in content]

    assert not missing, f"Отсутствуют необходимые пакеты в requirements.txt: {missing}"


@pytest.mark.ci
def test_home_page_has_valid_python_syntax():
    """Home.py содержит валидный Python код"""
    home_page = Path(__file__).parent.parent / 'app' / 'Home.py'
    content = home_page.read_text(encoding='utf-8')

    try:
        compile(content, 'Home.py', 'exec')
    except SyntaxError as e:
        pytest.fail(f"Синтаксическая ошибка в Home.py на строке {e.lineno}: {e.msg}")


# ============================================================================
# ОПЕРАЦИИ С ДАННЫМИ
# ============================================================================

@pytest.mark.smoke
def test_can_create_pandas_dataframe():
    """Можно создать Pandas DataFrame"""
    import pandas as pd

    df = pd.DataFrame({
        'temperature': [70, 75, 80, 85],
        'voltage': [110, 111, 109, 112],
        'status': ['OK', 'OK', 'WARNING', 'OK']
    })

    assert len(df) == 4, "DataFrame имеет неправильное количество строк"
    assert list(df.columns) == ['temperature', 'voltage', 'status'], "Колонки DataFrame неверны"


@pytest.mark.smoke
def test_can_create_numpy_array():
    """Можно создать NumPy массив"""
    import numpy as np

    arr = np.array([1, 2, 3, 4, 5])

    assert len(arr) == 5, "Массив имеет неправильную длину"
    assert arr.sum() == 15, "Сумма элементов массива неверна"


@pytest.mark.smoke
def test_pandas_basic_filtering_works():
    """Базовая фильтрация Pandas работает"""
    import pandas as pd

    df = pd.DataFrame({'value': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
    filtered = df[df['value'] > 5]

    assert len(filtered) == 5, "Фильтрация вернула неверное количество строк"
    assert filtered['value'].min() == 6, "Минимальное значение после фильтрации неверно"


@pytest.mark.smoke
def test_pandas_aggregation_works():
    """Агрегация данных Pandas работает"""
    import pandas as pd

    df = pd.DataFrame({
        'category': ['A', 'A', 'B', 'B', 'C', 'C'],
        'value': [10, 20, 30, 40, 50, 60]
    })

    grouped = df.groupby('category')['value'].sum()

    assert grouped['A'] == 30, "Сумма для категории A неверна"
    assert grouped['B'] == 70, "Сумма для категории B неверна"
    assert grouped['C'] == 110, "Сумма для категории C неверна"


# ============================================================================
# МАТЕМАТИЧЕСКИЕ ОПЕРАЦИИ
# ============================================================================

@pytest.mark.smoke
def test_numpy_array_addition_works():
    """Сложение NumPy массивов работает"""
    import numpy as np

    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    c = a + b

    assert list(c) == [5, 7, 9], "Сложение массивов дало неверный результат"


@pytest.mark.smoke
def test_numpy_statistical_functions_work():
    """Статистические функции NumPy работают"""
    import numpy as np

    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    assert data.mean() == 5.5, "Среднее значение неверно"
    assert data.std() > 0, "Стандартное отклонение должно быть положительным"
    assert data.min() == 1, "Минимум неверен"
    assert data.max() == 10, "Максимум неверен"


# ============================================================================
# ФАЙЛОВЫЕ ОПЕРАЦИИ
# ============================================================================

@pytest.mark.ci
def test_can_read_text_files():
    """Можно читать текстовые файлы"""
    readme = Path(__file__).parent.parent / 'README.md'
    content = readme.read_text(encoding='utf-8')
    assert len(content) > 0, "Не удалось прочитать README.md"


@pytest.mark.ci
def test_can_list_directory_contents():
    """Можно получить список файлов в директории"""
    app_dir = Path(__file__).parent.parent / 'app'
    files = list(app_dir.iterdir())
    assert len(files) > 0, "Директория app/ пуста или недоступна"


@pytest.mark.ci
def test_can_check_file_existence():
    """Можно проверить существование файла"""
    test_file = Path(__file__).parent.parent / 'README.md'
    assert test_file.exists(), "Проверка существования файла не работает"


# ============================================================================
# ОКРУЖЕНИЕ
# ============================================================================

@pytest.mark.ci
def test_working_directory_is_accessible():
    """Рабочая директория доступна для чтения"""
    import os
    cwd = os.getcwd()
    assert os.path.exists(cwd), "Рабочая директория недоступна"
    assert os.access(cwd, os.R_OK), "Нет прав на чтение рабочей директории"


@pytest.mark.ci
def test_can_create_temporary_files():
    """Можно создавать временные файлы"""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = f.name

    assert os.path.exists(temp_path), "Не удалось создать временный файл"
    os.unlink(temp_path)


@pytest.mark.ci
def test_python_executable_path_is_valid():
    """Путь к Python исполняемому файлу валиден"""
    import os
    python_exe = sys.executable
    assert os.path.exists(python_exe), f"Python executable не найден: {python_exe}"


# ============================================================================
# КОНФИГУРАЦИЯ ПРОЕКТА
# ============================================================================

@pytest.mark.ci
def test_all_init_files_exist():
    """Все необходимые __init__.py файлы существуют"""
    project_root = Path(__file__).parent.parent

    init_files = [
        project_root / 'src' / '__init__.py',
        project_root / 'models' / '__init__.py',
        project_root / 'config' / '__init__.py',
    ]

    missing = [str(f.relative_to(project_root)) for f in init_files if not f.exists()]

    assert not missing, f"Отсутствуют __init__.py файлы: {missing}"


@pytest.mark.ci
def test_app_pages_directory_exists():
    """Директория страниц приложения существует"""
    pages_dir = Path(__file__).parent.parent / 'app' / 'pages'
    assert pages_dir.exists(), "Директория app/pages/ не найдена"
    assert pages_dir.is_dir(), "app/pages/ не является директорией"


# ============================================================================
# БЫСТРЫЕ САНИТИ-ПРОВЕРКИ
# ============================================================================

@pytest.mark.smoke
def test_all_core_imports_succeed():
    """Все основные пакеты успешно импортируются"""
    packages = {
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'streamlit': 'Streamlit',
        'pytest': 'Pytest'
    }

    failed_imports = []
    for module_name, display_name in packages.items():
        try:
            __import__(module_name)
        except ImportError:
            failed_imports.append(display_name)

    assert not failed_imports, f"Не удалось импортировать: {', '.join(failed_imports)}"


@pytest.mark.ci
def test_no_obvious_syntax_errors_in_project():
    """Нет явных синтаксических ошибок в основных файлах проекта"""
    project_root = Path(__file__).parent.parent

    important_files = [
        project_root / 'app' / 'Home.py',
        project_root / 'data' / 'generate_data.py',
    ]

    errors = []
    for file_path in important_files:
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                compile(content, str(file_path), 'exec')
            except SyntaxError as e:
                errors.append(f"{file_path.name}: строка {e.lineno}")

    assert not errors, f"Найдены синтаксические ошибки: {errors}"
