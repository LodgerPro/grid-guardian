# 🎯 Первый Запуск GitHub Actions - Пошаговая Инструкция

## ✅ Чеклист Перед Запуском

Перед тем как запустить workflows, убедитесь:

- [ ] Репозиторий создан на GitHub
- [ ] Код закоммичен и запушен
- [ ] У вас есть права администратора репозитория
- [ ] GitHub Actions включены (обычно по умолчанию)

---

## 🚀 Шаг 1: Первый Push (Запуск CI)

### 1.1 Коммит и Push Workflows

```bash
# Проверить статус
git status

# Добавить все файлы workflows
git add .github/

# Коммит
git commit -m "ci: добавить GitHub Actions workflows

- CI тестирование (Python 3.9-3.13)
- Docker build и публикация
- Code quality проверки
- Release automation
- Scheduled тесты
- Security scanning
- Dependabot интеграция
"

# Push в main
git push origin main
```

### 1.2 Проверка Запуска

Перейдите в:
```
https://github.com/[USERNAME]/grid-guardian/actions
```

Вы должны увидеть запущенные workflows:
- ✅ CI - Tests & Quality Checks
- ✅ Docker Build & Push
- ✅ Code Quality & Linting
- ✅ CodeQL Security Analysis

**Ожидаемое время:** 15-20 минут для завершения всех проверок

---

## 🔧 Шаг 2: Настройка Permissions

### 2.1 Workflow Permissions

```
Settings → Actions → General → Workflow permissions
```

**Выберите:**
- ⚪ Read repository contents and packages permissions
- 🔘 **Read and write permissions** ← Выберите это!

**Также включите:**
- ✅ Allow GitHub Actions to create and approve pull requests

**Нажмите:** Save

### 2.2 Зачем это нужно?

Это позволяет workflows:
- Публиковать Docker образы в GitHub Container Registry
- Создавать GitHub Releases автоматически
- Обновлять PR статусы
- Загружать артефакты

---

## 🔐 Шаг 3: Настройка Секретов (Опционально)

### 3.1 Codecov Token (Для Coverage Reports)

1. Зарегистрируйтесь на [codecov.io](https://codecov.io)
2. Добавьте ваш репозиторий
3. Скопируйте токен

**Добавить в GitHub:**
```
Settings → Secrets and variables → Actions → New repository secret
```

- **Name:** `CODECOV_TOKEN`
- **Value:** [ваш токен]

### 3.2 Docker Hub (Опционально)

Если хотите публиковать в Docker Hub:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Создайте два секрета:**

1. **DOCKERHUB_USERNAME**
   - Value: ваш Docker Hub username

2. **DOCKERHUB_TOKEN**
   - Value: [создать на hub.docker.com/settings/security]

---

## 🛡️ Шаг 4: Настройка Branch Protection

### 4.1 Защитить Main Branch

```
Settings → Branches → Add branch protection rule
```

**Branch name pattern:** `main`

**Настройки:**

✅ **Require a pull request before merging**
   - Required approvals: 1

✅ **Require status checks to pass before merging**
   - Status checks found: (подождите первого CI run)
   - После первого run выберите:
     - `test (ubuntu-latest, 3.13)`
     - `lint`
     - `build-and-test`

✅ **Require conversation resolution before merging**

✅ **Do not allow bypassing the above settings**

**Нажмите:** Create

### 4.2 Зачем это нужно?

- Предотвращает прямые push в main
- Требует прохождения всех тестов
- Обеспечивает code review

---

## 🏷️ Шаг 5: Настройка Dependabot

Dependabot уже настроен через [`.github/dependabot.yml`](.github/dependabot.yml)

### 5.1 Включить Dependabot Alerts

```
Settings → Security → Code security and analysis
```

**Включите:**
- ✅ Dependabot alerts
- ✅ Dependabot security updates

### 5.2 Что будет происходить?

- Каждый понедельник Dependabot проверит обновления
- Создаст PR для outdated dependencies
- Minor и patch обновления будут auto-merged
- Major updates потребуют ручного review

---

## 🧪 Шаг 6: Первый Pull Request

### 6.1 Создать Тестовый PR

```bash
# Создать ветку
git checkout -b test/first-pr

# Внести небольшое изменение
echo "# Test PR" >> test.md

# Коммит
git add test.md
git commit -m "docs: добавить тестовый файл"

# Push
git push origin test/first-pr
```

### 6.2 Создать PR на GitHub

```
https://github.com/[USERNAME]/grid-guardian/compare/test/first-pr
```

**Нажмите:** Create pull request

### 6.3 Что произойдет?

1. ✅ **PR Auto-Labeler** добавит метки
2. ✅ **CI Tests** запустятся автоматически
3. ✅ **Code Quality** проверит изменения
4. ✅ **Docker Build** протестирует сборку

Подождите ~15 минут и проверьте, что все checks зеленые ✅

---

## 🎉 Шаг 7: Первый Release

### 7.1 Создать Release Tag

```bash
# Вернуться на main
git checkout main
git pull origin main

# Создать тег
git tag -a v1.0.0 -m "Release v1.0.0: Initial release with full CI/CD

Основные возможности:
- Автоматическое тестирование на Python 3.9-3.13
- Docker контейнеризация
- Code quality проверки
- 92 comprehensive теста
- Полная документация

Workflows:
- CI/CD pipeline
- Docker automation
- Security scanning
- Scheduled monitoring
"

# Push тега
git push origin v1.0.0
```

### 7.2 Что произойдет?

1. 📦 **Release Workflow** автоматически запустится
2. 🏗️ Создастся GitHub Release
3. 📚 Сгенерируется changelog
4. 🐳 Соберутся Docker образы с тегами
5. 📦 Создадутся tar.gz и zip архивы

**Время:** ~20-25 минут

### 7.3 Проверить Release

```
https://github.com/[USERNAME]/grid-guardian/releases
```

Вы должны увидеть:
- ✅ Release v1.0.0
- ✅ Release notes
- ✅ Assets (tar.gz, zip)
- ✅ Docker image tags

---

## 📊 Шаг 8: Проверка Результатов

### 8.1 Actions Dashboard

```
Repository → Actions
```

**Проверьте:**
- ✅ Все workflows завершились успешно
- ✅ Нет failed runs
- ✅ Artifacts загружены

### 8.2 Security Tab

```
Repository → Security → Code scanning
```

**Должны быть:**
- ✅ CodeQL analysis results
- ✅ No critical vulnerabilities
- ✅ Dependabot alerts (если есть)

### 8.3 Packages

```
Repository → Packages или
https://github.com/[USERNAME]?tab=packages
```

**Должен быть:**
- ✅ grid-guardian Docker image
- ✅ Tags: latest, v1.0.0

### 8.4 Coverage Reports

Если настроили Codecov:
```
https://codecov.io/gh/[USERNAME]/grid-guardian
```

**Проверьте:**
- ✅ Coverage badge
- ✅ Coverage percentage
- ✅ Coverage trends

---

## 🎨 Шаг 9: Добавить Badges в README

Обновите ваш [README.md](../README.md):

```markdown
# Grid Guardian

![CI Tests](https://github.com/[USERNAME]/grid-guardian/workflows/CI%20-%20Tests%20%26%20Quality%20Checks/badge.svg)
![Docker Build](https://github.com/[USERNAME]/grid-guardian/workflows/Docker%20Build%20%26%20Push/badge.svg)
![Code Quality](https://github.com/[USERNAME]/grid-guardian/workflows/Code%20Quality%20%26%20Linting/badge.svg)
![Security](https://github.com/[USERNAME]/grid-guardian/workflows/CodeQL%20Security%20Analysis/badge.svg)
[![codecov](https://codecov.io/gh/[USERNAME]/grid-guardian/branch/main/graph/badge.svg)](https://codecov.io/gh/[USERNAME]/grid-guardian)
```

**Замените `[USERNAME]` на ваш GitHub username!**

---

## 📅 Шаг 10: Мониторинг

### 10.1 Scheduled Workflows

Следующие workflows запустятся автоматически:

**Ежедневно в 3:00 UTC (6:00 MSK):**
- Scheduled Tests & Health Check
- Full test suite
- Dependency updates check

**Еженедельно в понедельник 9:00 UTC:**
- Dependency Update Check
- Outdated packages report

**Еженедельно в среду 6:00 UTC:**
- CodeQL Security Analysis
- Secret scanning

### 10.2 Email Notifications

Настройте уведомления:

```
Settings → Notifications → Actions
```

**Рекомендуемые настройки:**
- ✅ Send notifications for failed workflows only
- ✅ Include workflow run details

---

## ✅ Финальный Checklist

После выполнения всех шагов, убедитесь:

- [x] Workflows успешно запустились
- [x] Permissions настроены (read and write)
- [x] Branch protection включена для main
- [x] Dependabot активирован
- [x] Первый PR создан и merged
- [x] Первый release создан (v1.0.0)
- [x] Docker images опубликованы
- [x] Security scanning работает
- [x] Badges добавлены в README
- [x] Notifications настроены

---

## 🎓 Следующие Шаги

### Изучить Документацию

1. [📖 Workflows README](.github/workflows/README.md) - Полная документация
2. [⚡ Quick Start Guide](.github/QUICKSTART_CI.md) - Быстрый старт
3. [📊 Workflows Summary](.github/WORKFLOWS_SUMMARY.md) - Обзор всех workflows

### Локальная Разработка

```bash
# Запустить тесты локально
pytest tests/ -v

# Проверить код
ruff check app/ src/
black --check app/ src/

# Собрать Docker локально
docker build -t grid-guardian .
docker run -p 8501:8501 grid-guardian
```

### Кастомизация

- Изменить schedule в `.github/workflows/scheduled-tests.yml`
- Добавить новые проверки в `.github/workflows/code-quality.yml`
- Настроить notification channels

---

## 🐛 Troubleshooting

### Workflow Failed

```bash
# Проверить логи
gh run list
gh run view [run-id] --log

# Или через UI
Actions → Failed run → View logs
```

### Permission Errors

```
Settings → Actions → General → Workflow permissions
→ Read and write permissions
```

### Docker Push Failed

Проверьте:
- Включены GitHub Packages
- Permissions для packages (write)
- Docker login работает

### Tests Failing

```bash
# Запустить локально
pytest tests/ -v --tb=short

# Проверить зависимости
pip install -r requirements.txt --upgrade
```

---

## 📞 Поддержка

**Вопросы?**
- Проверьте [Workflows README](.github/workflows/README.md)
- Откройте [Issue](https://github.com/[USERNAME]/grid-guardian/issues)
- Изучите [GitHub Actions Docs](https://docs.github.com/actions)

---

## 🎉 Поздравляем!

Ваш CI/CD pipeline полностью настроен и работает!

**Что у вас теперь есть:**
- ✅ Автоматическое тестирование на каждый commit
- ✅ Docker автоматизация
- ✅ Code quality проверки
- ✅ Security scanning
- ✅ Automated releases
- ✅ Dependency monitoring
- ✅ Scheduled health checks

**Время настройки:** ~30 минут
**Экономия времени в будущем:** Бесценно! 🚀

---

**Последнее обновление:** 2026-01-23
**Версия:** 1.0
**Автор:** Grid Guardian Team
