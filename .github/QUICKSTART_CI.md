# ⚡ GitHub Actions - Быстрый Старт

Краткое руководство по настройке и использованию CI/CD для Grid Guardian.

## 🚀 Первоначальная Настройка (5 минут)

### Шаг 1: Включить GitHub Actions

Actions включены автоматически для публичных репозиториев. Для приватных:

```
Settings → Actions → General → Allow all actions
```

### Шаг 2: Настроить Permissions

```
Settings → Actions → General → Workflow permissions
→ ✅ Read and write permissions
→ ✅ Allow GitHub Actions to create and approve pull requests
```

### Шаг 3: Добавить Секреты (Опционально)

Для расширенной функциональности:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Codecov (для coverage reports):**
- Name: `CODECOV_TOKEN`
- Value: [получить на codecov.io]

**Docker Hub (для публикации):**
- Name: `DOCKERHUB_USERNAME`
- Value: ваш username
- Name: `DOCKERHUB_TOKEN`
- Value: [создать на hub.docker.com]

### Шаг 4: Защитить Main Branch

```
Settings → Branches → Add branch protection rule
```

**Настройки:**
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - Выбрать: `test`, `lint`, `docker-build`
- ✅ Require conversation resolution before merging

---

## 📋 Что Запускается Автоматически?

### При Push в Main/Develop

✅ **CI Tests** - полное тестирование
✅ **Code Quality** - проверка качества кода
✅ **Docker Build** - сборка и тестирование образа

### При Pull Request

✅ **CI Tests** - тестирование изменений
✅ **Code Quality** - проверка стиля и качества
✅ **Docker Build** - тест Docker образа
✅ **PR Labeler** - автоматические метки

### При Push Тега (v*.*.*)

✅ **Release** - создание релиза
✅ **Docker Release** - публикация образов
✅ **Build Artifacts** - создание архивов

### Каждый День в 3:00 UTC

✅ **Scheduled Tests** - ночное тестирование
✅ **Dependency Check** - проверка обновлений
✅ **Performance Benchmarks** - бенчмарки

---

## 🔄 Типичные Рабочие Процессы

### 1. Работа над Feature

```bash
# Создать ветку
git checkout -b feature/new-feature

# Внести изменения
# ... edit files ...

# Коммит и push
git add .
git commit -m "feat: добавить новую функцию"
git push origin feature/new-feature

# Создать PR на GitHub
# → CI автоматически запустится
```

**Что происходит:**
1. ✅ Запускаются тесты на Python 3.9-3.13
2. ✅ Проверяется качество кода
3. ✅ Тестируется Docker сборка
4. ✅ Автоматически добавляются метки

### 2. Создание Релиза

```bash
# Убедитесь, что main актуален
git checkout main
git pull origin main

# Создать тег
git tag -a v1.0.0 -m "Release v1.0.0: Major features"
git push origin v1.0.0

# → Release workflow автоматически запустится
```

**Что происходит:**
1. 📦 Создается GitHub Release
2. 🏗️ Собираются артефакты (tar.gz, zip)
3. 🐳 Публикуются Docker образы
4. ✅ Тестируется релиз на разных платформах

### 3. Исправление Бага

```bash
# Создать hotfix ветку
git checkout -b hotfix/critical-bug

# Исправить баг
# ... fix bug ...

# Коммит с правильным префиксом
git add .
git commit -m "fix: исправить критический баг в процессинге"
git push origin hotfix/critical-bug

# Создать PR с меткой priority
# → CI запустится автоматически
```

---

## 📊 Просмотр Результатов

### GitHub Actions Tab

```
Repository → Actions → Select workflow → Select run
```

**Вы увидите:**
- ✅ Статус каждого job
- 📝 Логи выполнения
- 📦 Артефакты (coverage, reports)
- ⏱️ Время выполнения

### Artifacts

Скачать отчеты:

```
Actions → Run → Artifacts section → Download
```

**Доступные артефакты:**
- `test-results-*` - результаты тестов
- `coverage-*` - coverage отчеты
- `security-reports` - отчеты безопасности
- `performance-benchmarks` - бенчмарки

### Pull Request Checks

В PR видны все проверки:

```
PR → Checks tab
```

- ✅ Зеленая галочка - все ОК
- ❌ Красный крест - есть проблемы
- 🟡 Желтый круг - выполняется

---

## 🐛 Частые Проблемы

### Problem: Тесты падают в CI, но работают локально

**Решение:**
```bash
# Проверить версию Python
python --version  # должна быть 3.9+

# Переустановить зависимости
pip install -r requirements.txt --upgrade

# Запустить тесты локально с такими же флагами
pytest tests/ -v --tb=short
```

### Problem: Docker build fails

**Решение:**
```bash
# Локальная сборка для отладки
docker build -t test .

# Проверить логи
docker build -t test . 2>&1 | tee build.log

# Проверить .dockerignore
cat .dockerignore
```

### Problem: Permission denied в workflow

**Решение:**
```
Settings → Actions → General → Workflow permissions
→ Выбрать "Read and write permissions"
```

### Problem: Codecov не работает

**Решение:**
1. Зарегистрироваться на codecov.io
2. Добавить репозиторий
3. Скопировать токен
4. Добавить в Secrets как `CODECOV_TOKEN`

---

## 🎯 Best Practices

### Commit Messages

Используйте conventional commits:

```
feat: новая функциональность
fix: исправление бага
docs: обновление документации
test: добавление тестов
refactor: рефакторинг кода
perf: улучшение производительности
ci: изменения CI/CD
chore: рутинные задачи
```

### Pull Requests

**Хороший PR:**
- ✅ Описательный title
- ✅ Детальное description
- ✅ Все тесты проходят
- ✅ Размер < 500 строк
- ✅ Один логический change

**Плохой PR:**
- ❌ "Update code"
- ❌ Нет описания
- ❌ Failing tests
- ❌ 2000+ строк изменений
- ❌ Смешаны разные изменения

### Версионирование

Следуйте Semantic Versioning:

```
v1.0.0 → MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: Новая функциональность (обратно совместима)
PATCH: Bug fixes
```

**Примеры:**
- `v1.0.0` → Первый стабильный релиз
- `v1.1.0` → Добавили новую страницу
- `v1.1.1` → Исправили баг
- `v2.0.0` → Изменили API (breaking)

---

## 📈 Мониторинг CI/CD

### Проверка Здоровья

```bash
# Статус последних runs
gh run list --limit 10

# Детали конкретного run
gh run view [run-id]

# Логи
gh run view [run-id] --log
```

### Badges для README

Добавьте в README.md:

```markdown
![CI Tests](https://github.com/USERNAME/grid-guardian/workflows/CI%20-%20Tests%20%26%20Quality%20Checks/badge.svg)
![Docker](https://github.com/USERNAME/grid-guardian/workflows/Docker%20Build%20%26%20Push/badge.svg)
![Quality](https://github.com/USERNAME/grid-guardian/workflows/Code%20Quality%20%26%20Linting/badge.svg)
```

### Email Уведомления

Настроить в:
```
Settings → Notifications → Actions
→ ✅ Send notifications for failed workflows
```

---

## 🔧 Кастомизация Workflows

### Отключить Определенные Jobs

Добавьте в workflow файл:

```yaml
jobs:
  my-job:
    if: github.event_name != 'pull_request'  # Только не для PR
    # ...
```

### Изменить Schedule

В `scheduled-tests.yml`:

```yaml
on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM UTC ежедневно
    # '0 */6 * * *'      # Каждые 6 часов
    # '0 0 * * 0'        # Каждое воскресенье
```

### Добавить Новый Workflow

```bash
# Создать файл
touch .github/workflows/my-workflow.yml

# Базовая структура
cat > .github/workflows/my-workflow.yml << 'EOF'
name: My Custom Workflow

on:
  push:
    branches: [ main ]

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run custom script
      run: echo "Hello!"
EOF
```

---

## 📚 Дополнительные Команды

### GitHub CLI

```bash
# Установить gh CLI
# https://cli.github.com/

# Список workflows
gh workflow list

# Запустить workflow вручную
gh workflow run ci.yml

# Просмотр runs
gh run list --workflow=ci.yml

# Скачать artifacts
gh run download [run-id]
```

### Локальное Тестирование Workflows

```bash
# Установить act
# https://github.com/nektos/act

# Запустить workflow локально
act -j test

# С секретами
act -j test -s GITHUB_TOKEN=xxx
```

---

## 🎓 Обучающие Ресурсы

### Официальная Документация
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

### Примеры
- [Actions Examples](https://github.com/actions/starter-workflows)
- [Awesome Actions](https://github.com/sdras/awesome-actions)

### Наши Workflows
- [CI Workflow](.github/workflows/ci.yml)
- [Docker Workflow](.github/workflows/docker.yml)
- [Полная Документация](.github/workflows/README.md)

---

## ✅ Checklist Первого Запуска

- [ ] Включить GitHub Actions
- [ ] Настроить permissions (read and write)
- [ ] Сделать первый commit
- [ ] Проверить, что workflows запустились
- [ ] Добавить branch protection для main
- [ ] Настроить Codecov (опционально)
- [ ] Создать первый Pull Request
- [ ] Проверить, что все checks проходят
- [ ] Добавить badges в README
- [ ] Создать тестовый релиз

---

## 🆘 Получить Помощь

**Если что-то не работает:**

1. Проверьте [Actions logs](https://github.com/USERNAME/grid-guardian/actions)
2. Изучите [Troubleshooting](.github/workflows/README.md#troubleshooting)
3. Откройте [Issue](https://github.com/USERNAME/grid-guardian/issues)
4. Проверьте [GitHub Status](https://www.githubstatus.com/)

---

**🎉 Готово! Ваш CI/CD pipeline настроен и работает!**

Теперь каждый push автоматически тестируется, проверяется и готов к развертыванию.
