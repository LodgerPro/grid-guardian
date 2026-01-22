# 🔄 GitHub Actions Workflows - Полный Обзор

## 📊 Статистика Workflows

| Workflow | Файл | Триггеры | Частота | Критичность |
|----------|------|----------|---------|-------------|
| CI Tests | `ci.yml` | Push, PR | На каждый commit | 🔴 Высокая |
| Docker Build | `docker.yml` | Push, PR, Tags | На каждый commit | 🔴 Высокая |
| Code Quality | `code-quality.yml` | Push, PR | На каждый commit | 🟡 Средняя |
| Release | `release.yml` | Tags | При создании релиза | 🔴 Высокая |
| Scheduled Tests | `scheduled-tests.yml` | Cron | Ежедневно 3:00 UTC | 🟢 Низкая |
| PR Labeler | `pr-labeler.yml` | PR open/sync | При PR операциях | 🟢 Низкая |
| Dependency Update | `dependency-update.yml` | Cron | Еженедельно ПН | 🟡 Средняя |
| CodeQL Analysis | `codeql-analysis.yml` | Push, PR, Cron | Еженедельно СР | 🟡 Средняя |

**Всего workflows:** 8
**Автоматических проверок:** 6
**Scheduled jobs:** 2

---

## 🎯 Основные Workflows

### 1. CI - Tests & Quality Checks

**Цель:** Обеспечение качества кода через автоматическое тестирование

**Jobs:**
1. **test** (Matrix: 10 комбинаций)
   - Python 3.9, 3.10, 3.11, 3.12, 3.13
   - Ubuntu + Windows
   - Генерация данных
   - Preprocessing + Feature engineering
   - Pytest с coverage
   - Upload в Codecov

2. **integration-test**
   - Полный pipeline запуск
   - Интеграционные тесты
   - Валидация data flow

3. **performance-test**
   - Performance benchmarks
   - Тесты скорости
   - Метрики производительности

4. **security-scan**
   - Bandit security check
   - Safety vulnerability scan
   - Отчеты безопасности

5. **notify**
   - Summary generation
   - Статус всех jobs

**Время выполнения:** ~15-20 минут
**Параллельных jobs:** До 10
**Артефакты:** Test reports, Coverage, Security reports

---

### 2. Docker Build & Push

**Цель:** Автоматическая сборка и публикация Docker образов

**Jobs:**
1. **build-and-test**
   - Multi-stage Docker build
   - Buildx для multi-platform
   - Тестирование образа
   - Health check контейнера
   - Push в ghcr.io
   - SBOM generation

2. **docker-compose-test**
   - Тест docker-compose
   - Проверка сервисов
   - Integration validation

3. **vulnerability-scan**
   - Trivy security scan
   - SARIF upload в GitHub
   - Vulnerability reporting

4. **summary**
   - Статус сборки
   - Информация об образах

**Образы:**
```
ghcr.io/[user]/grid-guardian:latest
ghcr.io/[user]/grid-guardian:main
ghcr.io/[user]/grid-guardian:sha-abc123
```

**Время выполнения:** ~10-15 минут
**Размер образа:** ~800MB (сжатый)
**Platforms:** linux/amd64, linux/arm64

---

### 3. Code Quality & Linting

**Цель:** Поддержание высокого качества кода

**Jobs:**
1. **lint** - Ruff, Flake8, Pylint
2. **format-check** - Black, isort
3. **type-check** - mypy
4. **complexity** - Radon, Xenon
5. **dependency-check** - pip-audit
6. **docs-check** - pydocstyle
7. **summary** - Общий статус

**Проверяемые метрики:**
- PEP 8 compliance
- Type hints coverage
- Cyclomatic complexity < 10
- Maintainability index > B
- Security vulnerabilities
- Docstring coverage

**Время выполнения:** ~5-8 минут

---

### 4. Release & Deploy

**Цель:** Автоматизация процесса релиза

**Jobs:**
1. **create-release**
   - GitHub Release
   - Changelog generation
   - Release notes

2. **build-artifacts**
   - Distribution packages
   - tar.gz, zip archives
   - Полные данные

3. **test-release**
   - Multi-platform тесты
   - Dependency validation

4. **docker-release**
   - Production образы
   - Version tags
   - Latest tag

5. **notify**
   - Release summary
   - Download links

**Артефакты релиза:**
- `grid-guardian-v1.0.0.tar.gz`
- `grid-guardian-v1.0.0.zip`
- Docker images с версией

**Время выполнения:** ~20-25 минут

---

### 5. Scheduled Tests & Health Check

**Цель:** Регулярная проверка здоровья проекта

**Jobs:**
1. **nightly-tests** - Полный test suite
2. **dependency-updates** - Проверка обновлений
3. **performance-benchmark** - Бенчмарки
4. **docker-health** - Проверка образа
5. **repository-health** - Структура проекта

**Schedule:** Ежедневно в 3:00 UTC (6:00 MSK)

**Проверки:**
- Все 92 теста
- Outdated dependencies
- Security vulnerabilities
- Performance metrics
- Docker image health
- Repository structure

**Время выполнения:** ~30-40 минут

---

### 6. PR Auto-Labeler

**Цель:** Автоматическая маркировка Pull Requests

**Функции:**
- Label по измененным файлам
- Label по размеру PR (XS/S/M/L/XL)
- Проверка semantic commit
- Приветствие для новых контрибьюторов

**Labels:**
- `documentation`, `tests`, `ci/cd`
- `app`, `src`, `models`, `data`
- `size/XS` (< 10 lines) → `size/XL` (> 1000 lines)

**Время выполнения:** < 1 минута

---

### 7. Dependency Update Check

**Цель:** Мониторинг обновлений зависимостей

**Jobs:**
1. **check-updates**
   - Список outdated packages
   - Security audit
   - Reports generation

2. **dependabot-auto-merge**
   - Авто-merge patch updates
   - Авто-merge minor updates
   - Manual review для major

**Schedule:** Еженедельно в понедельник 9:00 UTC

**Интеграция с Dependabot:**
- Автоматические PR для обновлений
- Security alerts
- Version compatibility checks

---

### 8. CodeQL Security Analysis

**Цель:** Глубокий анализ безопасности кода

**Jobs:**
1. **analyze**
   - CodeQL Python analysis
   - Security queries
   - Quality queries
   - SARIF upload

2. **secret-scan**
   - TruffleHog scanning
   - Secret detection
   - Credential leaks

3. **security-summary**
   - Статус безопасности

**Schedule:** Еженедельно в среду 6:00 UTC

**Детекция:**
- SQL injection
- XSS vulnerabilities
- Path traversal
- Command injection
- Hard-coded credentials
- API keys and tokens

---

## 📈 Метрики и Мониторинг

### Средняя Статистика

| Метрика | Значение |
|---------|----------|
| Среднее время CI | 15 минут |
| Успешность | 95%+ |
| Тестов выполняется | 92+ |
| Code coverage | 85%+ |
| Workflows активных | 8 |
| Jobs на commit | 20+ |

### Использование Resources

**GitHub Actions минуты:**
- CI на commit: ~150 минут (10 matrix jobs × 15 min)
- Docker build: ~15 минут
- Code Quality: ~8 минут
- Scheduled (daily): ~40 минут
- **Итого в день:** ~250-300 минут

**Free tier:** 2000 минут/месяц
**Рекомендация:** ~9000 минут/месяц при активной разработке

---

## 🔐 Безопасность

### Security Checks

1. **Bandit** - Python security linter
2. **Safety** - Dependency vulnerabilities
3. **CodeQL** - Advanced code analysis
4. **Trivy** - Docker image scanning
5. **TruffleHog** - Secret detection
6. **pip-audit** - Package auditing

### Security Reports

Доступны в:
```
Security → Code scanning alerts
Security → Dependabot alerts
Security → Secret scanning alerts
```

---

## 🎓 Обучение и Документация

### Документы

1. **README.md** - Полная документация workflows
2. **QUICKSTART_CI.md** - Быстрый старт
3. **WORKFLOWS_SUMMARY.md** - Этот файл
4. **dependabot.yml** - Конфигурация Dependabot
5. **labeler.yml** - Конфигурация PR labels

### Примеры Использования

**Запуск workflow вручную:**
```bash
gh workflow run ci.yml
gh workflow run docker.yml --ref main
```

**Просмотр статуса:**
```bash
gh run list
gh run view [run-id]
```

**Скачать артефакты:**
```bash
gh run download [run-id]
```

---

## 🚀 Расширение Workflows

### Добавить Новый Workflow

```yaml
# .github/workflows/my-workflow.yml
name: My Custom Workflow

on:
  push:
    branches: [ main ]

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Custom step
        run: echo "Hello!"
```

### Добавить Новый Job

```yaml
jobs:
  existing-job:
    # ...

  new-job:
    needs: existing-job
    runs-on: ubuntu-latest
    steps:
      - name: New step
        run: echo "New job!"
```

---

## 📊 Dashboard и Визуализация

### GitHub Actions Tab

```
Repository → Actions
```

Показывает:
- Статус всех workflows
- История запусков
- Артефакты
- Время выполнения

### Insights

```
Repository → Insights → Community
```

Показывает:
- Issue statistics
- PR statistics
- Contributor activity

---

## 🎯 Roadmap

### Планируемые Улучшения

- [ ] Кэширование зависимостей между runs
- [ ] Parallel test execution
- [ ] Custom runners для faster builds
- [ ] Slack/Discord notifications
- [ ] Deployment workflows (staging/production)
- [ ] Performance regression tracking
- [ ] Automated changelog generation
- [ ] Release notes templates

---

## 📞 Поддержка

**Вопросы по Workflows:**
- Изучить логи в Actions tab
- Проверить документацию
- Открыть Issue с тегом `ci/cd`

**Полезные Ссылки:**
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Grid Guardian CI/CD Guide](.github/QUICKSTART_CI.md)

---

**Последнее обновление:** 2026-01-22
**Версия документации:** 1.0
**Автор:** Grid Guardian Team
