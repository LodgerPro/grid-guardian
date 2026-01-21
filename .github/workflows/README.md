# 🔄 GitHub Actions Workflows

Комплексная CI/CD система для автоматизации тестирования, сборки и развертывания Grid Guardian.

## 📋 Обзор Workflows

### 1. ✅ CI - Tests & Quality Checks (`ci.yml`)

**Триггеры:**
- Push в ветки `main`, `develop`
- Pull requests в `main`, `develop`
- Ручной запуск (workflow_dispatch)

**Задачи:**
- **Тестирование** на нескольких версиях Python (3.9-3.13) и ОС (Ubuntu, Windows)
- **Генерация данных** и запуск preprocessing
- **Покрытие кода** с отчетами и загрузкой в Codecov
- **Интеграционные тесты** - полный pipeline
- **Performance тесты** - бенчмарки производительности
- **Security scanning** - Bandit и Safety проверки
- **Артефакты** - HTML отчеты, coverage reports

**Матрица тестирования:**
```yaml
Python: 3.9, 3.10, 3.11, 3.12, 3.13
OS: Ubuntu Latest, Windows Latest
```

**Использование:**
```bash
# Автоматически запускается при push/PR
# Ручной запуск:
# Actions → CI - Tests & Quality Checks → Run workflow
```

---

### 2. 🐳 Docker Build & Push (`docker.yml`)

**Триггеры:**
- Push в ветку `main`
- Push тегов `v*.*.*`
- Pull requests в `main`
- Ручной запуск

**Задачи:**
- **Сборка образа** с multi-stage build
- **Тестирование образа** - запуск и health checks
- **Публикация** в GitHub Container Registry (ghcr.io)
- **Multi-platform** - amd64, arm64
- **Docker Compose тест** - проверка compose конфигурации
- **Security scan** - Trivy vulnerability scanning
- **SBOM генерация** - Software Bill of Materials

**Образы:**
```
ghcr.io/[username]/grid-guardian:latest
ghcr.io/[username]/grid-guardian:main
ghcr.io/[username]/grid-guardian:sha-[commit]
```

**Использование:**
```bash
# Автоматически при push в main
# Скачать образ:
docker pull ghcr.io/[username]/grid-guardian:latest
```

---

### 3. 📊 Code Quality & Linting (`code-quality.yml`)

**Триггеры:**
- Push в `main`, `develop`
- Pull requests в `main`, `develop`
- Ручной запуск

**Проверки:**

#### Linting
- **Ruff** - быстрый Python linter
- **Flake8** - style guide enforcement
- **Pylint** - code analysis

#### Форматирование
- **Black** - code formatter
- **isort** - import sorting

#### Типы
- **mypy** - static type checking

#### Сложность
- **Radon** - cyclomatic complexity, maintainability index
- **Xenon** - complexity thresholds

#### Безопасность
- **pip-audit** - dependency security

#### Документация
- **pydocstyle** - docstring conventions

**Использование:**
```bash
# Локально запустить проверки:
ruff check app/ src/
black --check app/ src/
mypy app/ src/
```

---

### 4. 🚀 Release & Deploy (`release.yml`)

**Триггеры:**
- Push тегов `v*.*.*`
- Ручной запуск с указанием версии

**Процесс:**

1. **Создание релиза**
   - Генерация changelog из коммитов
   - Создание GitHub Release
   - Автоматические release notes

2. **Сборка артефактов**
   - Генерация данных
   - Preprocessing и feature engineering
   - Создание tar.gz и zip архивов
   - Загрузка в Release

3. **Тестирование релиза**
   - Тест на Ubuntu и Windows
   - Проверка Python 3.9 и 3.13
   - Валидация зависимостей

4. **Docker релиз**
   - Сборка и публикация образов
   - Теги: latest, version, major, minor
   - Multi-platform (amd64, arm64)

**Создание релиза:**
```bash
# Создать тег
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Или через GitHub UI:
# Releases → Create new release → Choose tag
```

**Docker теги релиза:**
```
ghcr.io/[username]/grid-guardian:latest
ghcr.io/[username]/grid-guardian:1.0.0
ghcr.io/[username]/grid-guardian:1.0
ghcr.io/[username]/grid-guardian:1
```

---

### 5. 🌙 Scheduled Tests & Health Check (`scheduled-tests.yml`)

**Триггеры:**
- **Schedule** - каждый день в 3:00 UTC
- Ручной запуск

**Задачи:**

#### Ночное тестирование
- Полный test suite
- Свежая генерация данных
- Расширенные coverage отчеты

#### Проверка зависимостей
- Поиск устаревших пакетов
- Security audit
- Отчеты о vulnerabilities

#### Performance бенчмарки
- Тесты производительности
- Timeit benchmarks
- Исторические данные

#### Docker health
- Сборка образа
- Health check контейнера
- Проверка размера образа

#### Repository health
- Проверка структуры файлов
- Валидация синтаксиса Python
- Статистика кода

**Просмотр результатов:**
```
Actions → Scheduled Tests & Health Check → Latest run
```

---

## 🔧 Настройка

### Секреты GitHub

Для полной функциональности настройте секреты:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Обязательные:**
- `GITHUB_TOKEN` - автоматически доступен

**Опциональные:**
- `DOCKERHUB_USERNAME` - для публикации в Docker Hub
- `DOCKERHUB_TOKEN` - токен Docker Hub
- `CODECOV_TOKEN` - для загрузки coverage в Codecov

### Permissions

Убедитесь, что у workflows есть нужные права:

```
Settings → Actions → General → Workflow permissions
```

Выберите: **Read and write permissions**

### Branch Protection

Рекомендуемые правила для `main`:

```
Settings → Branches → Add branch protection rule
```

- ✅ Require pull request reviews
- ✅ Require status checks to pass:
  - CI - Tests
  - Code Quality
  - Docker Build
- ✅ Require branches to be up to date

---

## 📊 Статус Badges

Добавьте badges в README:

```markdown
![CI Tests](https://github.com/[username]/grid-guardian/workflows/CI%20-%20Tests%20%26%20Quality%20Checks/badge.svg)
![Docker Build](https://github.com/[username]/grid-guardian/workflows/Docker%20Build%20%26%20Push/badge.svg)
![Code Quality](https://github.com/[username]/grid-guardian/workflows/Code%20Quality%20%26%20Linting/badge.svg)
![Release](https://github.com/[username]/grid-guardian/workflows/Release%20%26%20Deploy/badge.svg)
```

---

## 🚦 Статусы Jobs

### ✅ Success
Все проверки прошли успешно.

### ⚠️ Warning
Некоторые необязательные проверки не прошли (continue-on-error: true).

### ❌ Failure
Критические проверки не прошли. Требуется исправление.

### 🔄 Running
Workflow выполняется.

---

## 📝 Best Practices

### 1. Commit Messages
```
feat: добавить новую функцию
fix: исправить баг
docs: обновить документацию
test: добавить тесты
ci: изменить CI/CD
```

### 2. Pull Requests
- Создавайте PR из feature веток
- Дождитесь прохождения всех проверок
- Запросите review

### 3. Releases
- Используйте semantic versioning (v1.0.0)
- Добавляйте описание изменений
- Тестируйте перед релизом

### 4. Docker Images
- Проверяйте размер образов
- Следите за security scan результатами
- Используйте конкретные теги в production

---

## 🐛 Troubleshooting

### Тесты падают локально, но проходят в CI

Проверьте:
- Версию Python
- Установленные зависимости
- Переменные окружения

```bash
# Синхронизировать окружение
pip install -r requirements.txt --upgrade
```

### Docker build fails

Проверьте:
- Dockerfile синтаксис
- Наличие всех файлов
- .dockerignore

```bash
# Локальная сборка для отладки
docker build -t grid-guardian-test .
docker run -p 8501:8501 grid-guardian-test
```

### Release workflow не запускается

Проверьте:
- Формат тега (должен быть v*.*.*)
- Push тега в remote
- Permissions для workflow

```bash
# Правильное создание тега
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 📚 Дополнительные Ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Official Actions](https://github.com/docker/build-push-action)
- [Python Testing Best Practices](https://docs.pytest.org/)
- [Semantic Versioning](https://semver.org/)

---

## 🔄 Обновление Workflows

Для обновления workflows:

1. Редактируйте файлы в `.github/workflows/`
2. Коммитьте изменения
3. Создайте PR для review
4. После merge workflows обновятся автоматически

**Важно:** Тестируйте изменения в feature ветке перед merge в main!

---

## 📞 Поддержка

Вопросы по CI/CD:
- Открыть [Issue](https://github.com/[username]/grid-guardian/issues)
- Проверить [Actions Logs](https://github.com/[username]/grid-guardian/actions)
- Изучить [Документацию проекта](../README.md)

---

**Создано для Grid Guardian Project**
*Автоматизация тестирования, качества кода и развертывания*
