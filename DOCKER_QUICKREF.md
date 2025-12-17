# 🐳 Grid Guardian - Docker Quick Reference

Быстрая справка по Docker командам для Grid Guardian.

## 🚀 Быстрый Старт

### Windows
```batch
docker-quickstart.bat
```

### Linux/Mac
```bash
docker-compose up -d && sleep 30 && open http://localhost:8501
```

## 📋 Основные Команды

### Управление Контейнером

```bash
# Запуск (фон)
docker-compose up -d

# Запуск (с логами)
docker-compose up

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка и запуск
docker-compose up -d --build
```

### Просмотр Статуса

```bash
# Список контейнеров
docker ps

# Статус Grid Guardian
docker-compose ps

# Проверка здоровья
docker inspect --format='{{.State.Health.Status}}' grid-guardian-app
```

### Логи

```bash
# Все логи (follow)
docker-compose logs -f

# Последние 100 строк
docker-compose logs --tail 100

# Только ошибки
docker-compose logs | grep ERROR
```

### Мониторинг

```bash
# CPU/Memory в реальном времени
docker stats grid-guardian-app

# Использование диска
docker system df
```

## 🔧 Частые Задачи

### Войти в Контейнер

```bash
# Bash shell
docker exec -it grid-guardian-app bash

# Python интерпретатор
docker exec -it grid-guardian-app python

# Запустить скрипт
docker exec -it grid-guardian-app python data/generate_data.py
```

### Проверить Данные

```bash
# Список файлов данных
docker exec grid-guardian-app ls -lh /app/data/raw/

# Проверить размер данных
docker exec grid-guardian-app python -c "import pandas as pd; df=pd.read_parquet('/app/data/raw/grid_telemetry_data.parquet'); print(f'{len(df):,} records')"
```

### Изменить Порт

В `docker-compose.yml`:
```yaml
ports:
  - "8080:8501"  # Новый порт:Внутренний порт
```

Затем:
```bash
docker-compose down
docker-compose up -d
```

## 🐛 Устранение Проблем

### Порт Занят

**Windows:**
```batch
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8501 | xargs kill -9
```

### Контейнер Не Запускается

```bash
# Просмотр ошибок
docker logs grid-guardian-app

# Полная пересборка
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Очистка Docker

```bash
# Удалить остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune -a

# Полная очистка (ОСТОРОЖНО!)
docker system prune -a --volumes
```

## 📊 Проверка Работоспособности

```bash
# 1. Контейнер запущен?
docker ps | grep grid-guardian

# 2. Здоров ли контейнер?
curl http://localhost:8501/_stcore/health

# 3. Приложение доступно?
curl -I http://localhost:8501

# 4. Логи без ошибок?
docker logs grid-guardian-app 2>&1 | grep -i error
```

## 🔐 Production Tips

### Автоматический Перезапуск

```yaml
restart: always  # В docker-compose.yml
```

### Ограничение Ресурсов

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### Backup Данных

```bash
# Создать backup
docker run --rm --volumes-from grid-guardian-app \
  -v $(pwd):/backup \
  busybox tar czf /backup/grid-guardian-backup.tar.gz /app/data

# Восстановить
docker run --rm --volumes-from grid-guardian-app \
  -v $(pwd):/backup \
  busybox tar xzf /backup/grid-guardian-backup.tar.gz -C /
```

## 📚 Ссылки

- [Полная документация](DOCKER.md)
- [README](README.md)
- [Тесты](tests/README.md)

## ⚡ Горячие Клавиши

```bash
# Алиасы для удобства (добавить в .bashrc или .zshrc)
alias gg-start='docker-compose up -d'
alias gg-stop='docker-compose down'
alias gg-restart='docker-compose restart'
alias gg-logs='docker-compose logs -f'
alias gg-status='docker ps | grep grid-guardian'
alias gg-shell='docker exec -it grid-guardian-app bash'
```

---

**Версия:** 1.0
**Python:** 3.13.7
**Docker:** 20.10+
