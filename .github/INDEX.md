# 📚 GitHub Actions - Индекс Документации

Полный список всех workflows, конфигураций и документации для Grid Guardian CI/CD.

---

## 📁 Структура `.github/`

```
.github/
├── workflows/               # GitHub Actions workflows
│   ├── ci.yml              # CI тестирование
│   ├── docker.yml          # Docker automation
│   ├── code-quality.yml    # Code quality checks
│   ├── release.yml         # Release automation
│   ├── scheduled-tests.yml # Scheduled monitoring
│   ├── pr-labeler.yml      # PR auto-labeling
│   ├── dependency-update.yml # Dependency monitoring
│   ├── codeql-analysis.yml # Security analysis
│   └── README.md           # Workflows документация
│
├── dependabot.yml          # Dependabot configuration
├── labeler.yml             # PR labeler configuration
│
├── FIRST_RUN.md            # Пошаговая инструкция первого запуска
├── QUICKSTART_CI.md        # Быстрый старт CI/CD
├── WORKFLOWS_SUMMARY.md    # Обзор всех workflows
└── INDEX.md                # Этот файл
```

---

## 🔄 Workflows (8 файлов)

### 1. `ci.yml` - CI Tests & Quality Checks
**Описание:** Основной CI pipeline для тестирования кода
**Триггеры:** Push (main, develop), Pull Requests
**Jobs:** 5 (test, integration-test, performance-test, security-scan, notify)
**Время выполнения:** ~15-20 минут

**Что делает:**
- Тестирование на Python 3.9-3.13
- Ubuntu и Windows
- Генерация данных и preprocessing
- Coverage reports (Codecov)
- Integration и performance тесты
- Security scanning (Bandit, Safety)

**Документация:** [ci.yml](workflows/ci.yml)

---

### 2. `docker.yml` - Docker Build & Push
**Описание:** Автоматическая сборка и публикация Docker образов
**Триггеры:** Push (main), Tags (v*.*.*), Pull Requests
**Jobs:** 4 (build-and-test, docker-compose-test, vulnerability-scan, summary)
**Время выполнения:** ~10-15 минут

**Что делает:**
- Multi-stage Docker build
- Multi-platform (amd64, arm64)
- Health checks
- Push в GitHub Container Registry
- Trivy security scanning
- Docker Compose тестирование

**Образы:** `ghcr.io/[user]/grid-guardian:latest`

**Документация:** [docker.yml](workflows/docker.yml)

---

### 3. `code-quality.yml` - Code Quality & Linting
**Описание:** Проверка качества кода и стиля
**Триггеры:** Push (main, develop), Pull Requests
**Jobs:** 7 (lint, format-check, type-check, complexity, dependency-check, docs-check, summary)
**Время выполнения:** ~5-8 минут

**Что делает:**
- Linting (Ruff, Flake8, Pylint)
- Formatting (Black, isort)
- Type checking (mypy)
- Complexity analysis (Radon, Xenon)
- Dependency audit (pip-audit)
- Docstring checking (pydocstyle)

**Документация:** [code-quality.yml](workflows/code-quality.yml)

---

### 4. `release.yml` - Release & Deploy
**Описание:** Автоматизация создания релизов
**Триггеры:** Push tags (v*.*.*), Manual dispatch
**Jobs:** 5 (create-release, build-artifacts, test-release, docker-release, notify)
**Время выполнения:** ~20-25 минут

**Что делает:**
- Создание GitHub Release
- Генерация changelog
- Сборка артефактов (tar.gz, zip)
- Multi-platform тестирование
- Docker images с версиями
- Release notes

**Документация:** [release.yml](workflows/release.yml)

---

### 5. `scheduled-tests.yml` - Scheduled Tests & Health
**Описание:** Регулярные проверки здоровья проекта
**Триггеры:** Cron (ежедневно 3:00 UTC), Manual dispatch
**Jobs:** 6 (nightly-tests, dependency-updates, performance-benchmark, docker-health, repository-health, notify)
**Время выполнения:** ~30-40 минут

**Что делает:**
- Полный test suite ночью
- Проверка outdated dependencies
- Security audit
- Performance benchmarks
- Docker health check
- Repository structure validation

**Документация:** [scheduled-tests.yml](workflows/scheduled-tests.yml)

---

### 6. `pr-labeler.yml` - PR Auto-Labeler
**Описание:** Автоматическая маркировка Pull Requests
**Триггеры:** PR (opened, synchronize, reopened)
**Jobs:** 1 (label)
**Время выполнения:** < 1 минута

**Что делает:**
- Label по измененным файлам
- Label по размеру PR (XS/S/M/L/XL)
- Semantic PR title проверка
- Приветствие для новых contributors

**Конфигурация:** [labeler.yml](labeler.yml)

**Документация:** [pr-labeler.yml](workflows/pr-labeler.yml)

---

### 7. `dependency-update.yml` - Dependency Updates
**Описание:** Мониторинг обновлений зависимостей
**Триггеры:** Cron (еженедельно ПН 9:00 UTC), Manual dispatch
**Jobs:** 2 (check-updates, dependabot-auto-merge)
**Время выполнения:** ~3-5 минут

**Что делает:**
- Список outdated packages
- Security audit
- Auto-merge minor/patch updates
- Reports generation

**Документация:** [dependency-update.yml](workflows/dependency-update.yml)

---

### 8. `codeql-analysis.yml` - CodeQL Security
**Описание:** Глубокий анализ безопасности кода
**Триггеры:** Push (main, develop), PR, Cron (еженедельно СР 6:00 UTC)
**Jobs:** 3 (analyze, secret-scan, security-summary)
**Время выполнения:** ~8-12 минут

**Что делает:**
- CodeQL Python analysis
- Security и quality queries
- Secret scanning (TruffleHog)
- SARIF upload в GitHub Security

**Документация:** [codeql-analysis.yml](workflows/codeql-analysis.yml)

---

## ⚙️ Конфигурационные Файлы (2 файла)

### `dependabot.yml` - Dependabot Configuration
**Описание:** Настройка автоматических обновлений зависимостей

**Отслеживает:**
- Python pip packages (еженедельно)
- GitHub Actions (еженедельно)
- Docker base images (еженедельно)

**Настройки:**
- Schedule: Понедельник 9:00 Europe/Moscow
- Open PR limit: 10 (pip), 5 (actions), 3 (docker)
- Auto-reviewers и assignees
- Semantic commit messages

**Документация:** [dependabot.yml](dependabot.yml)

---

### `labeler.yml` - PR Labeler Configuration
**Описание:** Правила для автоматической маркировки PR

**Labels:**
- `documentation` - изменения в *.md, docs/
- `tests` - изменения в tests/, *test*.py
- `ci/cd` - изменения в .github/, Dockerfile
- `app` - изменения в app/
- `src` - изменения в src/
- `models` - изменения в models/
- `data` - изменения в data/
- `config` - изменения в config/, requirements.txt
- `dependencies` - изменения в requirements.txt

**Документация:** [labeler.yml](labeler.yml)

---

## 📖 Документация (4 файла)

### 1. `workflows/README.md` - Workflows Documentation
**Размер:** ~10 KB
**Разделы:**
- Обзор всех workflows
- Подробное описание каждого workflow
- Настройка и конфигурация
- Troubleshooting
- Best practices
- Badges
- Дополнительные ресурсы

**Аудитория:** Разработчики, DevOps инженеры
**Читать:** [README.md](workflows/README.md)

---

### 2. `QUICKSTART_CI.md` - Quick Start Guide
**Размер:** ~12 KB
**Разделы:**
- Первоначальная настройка (5 минут)
- Что запускается автоматически
- Типичные рабочие процессы
- Просмотр результатов
- Частые проблемы
- Best practices
- Мониторинг CI/CD
- Кастомизация workflows

**Аудитория:** Новые пользователи
**Читать:** [QUICKSTART_CI.md](QUICKSTART_CI.md)

---

### 3. `WORKFLOWS_SUMMARY.md` - Workflows Summary
**Размер:** ~11 KB
**Разделы:**
- Статистика workflows
- Основные workflows (детальный обзор)
- Метрики и мониторинг
- Безопасность
- Обучение и документация
- Расширение workflows
- Dashboard и визуализация
- Roadmap

**Аудитория:** Все пользователи
**Читать:** [WORKFLOWS_SUMMARY.md](WORKFLOWS_SUMMARY.md)

---

### 4. `FIRST_RUN.md` - First Run Guide
**Размер:** ~14 KB
**Разделы:**
- Пошаговая инструкция (10 шагов)
- Первый push и запуск CI
- Настройка permissions
- Настройка секретов
- Branch protection
- Первый Pull Request
- Первый Release
- Проверка результатов
- Добавление badges
- Финальный checklist

**Аудитория:** Новые пользователи (первый раз)
**Читать:** [FIRST_RUN.md](FIRST_RUN.md)

---

### 5. `INDEX.md` - Documentation Index
**Размер:** ~8 KB
**Описание:** Этот файл - навигация по всей документации

---

## 🎯 Быстрая Навигация

### Я новый пользователь, с чего начать?
1. Прочитайте [FIRST_RUN.md](FIRST_RUN.md) - пошаговая инструкция
2. Затем [QUICKSTART_CI.md](QUICKSTART_CI.md) - быстрый старт

### Мне нужна информация о конкретном workflow
- [workflows/README.md](workflows/README.md) - подробное описание каждого

### Хочу понять общую картину
- [WORKFLOWS_SUMMARY.md](WORKFLOWS_SUMMARY.md) - обзор и статистика

### Что-то не работает
- [QUICKSTART_CI.md](QUICKSTART_CI.md#troubleshooting) - раздел Troubleshooting
- [workflows/README.md](workflows/README.md#troubleshooting) - подробный troubleshooting

### Хочу настроить или изменить workflows
- [workflows/README.md](workflows/README.md#конфигурация) - настройка
- Изучить файлы в [workflows/](workflows/)

---

## 📊 Статистика

**Всего файлов:** 14
- Workflows: 8
- Конфигурации: 2
- Документация: 4

**Общий размер:** ~100 KB

**Строк кода (workflows):** ~1,200
**Строк документации:** ~2,500

**Jobs всего:** 32
**Steps всего:** ~150

---

## 🔗 Полезные Ссылки

### Внутренние
- [Grid Guardian README](../README.md)
- [Testing Documentation](../tests/README.md)
- [Docker Documentation](../DOCKER.md)
- [Project Structure](../PROJECT_STRUCTURE.md)

### Внешние
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Codecov Action](https://github.com/codecov/codecov-action)

---

## 📅 История Обновлений

### v1.0 (2026-01-23)
- ✅ Создан полный набор workflows
- ✅ CI/CD для тестирования
- ✅ Docker automation
- ✅ Code quality checks
- ✅ Release automation
- ✅ Security scanning
- ✅ Scheduled monitoring
- ✅ Dependabot integration
- ✅ Comprehensive documentation

---

## 📞 Поддержка

**Вопросы по CI/CD:**
- Проверьте документацию выше
- Откройте [Issue](https://github.com/[USERNAME]/grid-guardian/issues) с тегом `ci/cd`
- Изучите логи в [Actions tab](https://github.com/[USERNAME]/grid-guardian/actions)

**Предложения по улучшению:**
- Создайте Issue с тегом `enhancement`
- Предложите Pull Request

---

## ✨ Краткая Справка

### Запуск workflow вручную
```bash
gh workflow run ci.yml
gh workflow run docker.yml --ref main
```

### Просмотр статуса
```bash
gh run list --limit 10
gh run view [run-id]
gh run view [run-id] --log
```

### Скачать артефакты
```bash
gh run download [run-id]
```

### Проверить workflows
```bash
gh workflow list
gh workflow view ci.yml
```

---

**Последнее обновление:** 2026-01-23
**Версия документации:** 1.0
**Автор:** Grid Guardian Team

---

**🎉 Добро пожаловать в Grid Guardian CI/CD!**

Вся необходимая документация теперь у вас под рукой.
