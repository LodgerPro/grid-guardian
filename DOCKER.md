# 🐳 Grid Guardian - Docker Deployment Guide

Полное руководство по развертыванию Grid Guardian в Docker контейнере.

## 📋 Системные Требования

### Обязательные
- **Docker Desktop 20.10+** ([Скачать](https://www.docker.com/products/docker-desktop))
- **Docker Compose 2.0+** (входит в Docker Desktop)

### Рекомендуемое Железо
- **CPU:** 2+ ядра
- **RAM:** 4GB минимум, 8GB рекомендуется
- **Диск:** 10GB свободного места
- **ОС:** Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)

## 🚀 Быстрый Старт

### Windows (Автоматический)

1. **Убедитесь что Docker Desktop запущен**

2. **Запустите скрипт:**
   ```batch
   docker-quickstart.bat
   ```

Скрипт автоматически:
- ✅ Проверит Docker
- ✅ Соберет образ
- ✅ Запустит контейнер
- ✅ Откроет браузер

### Linux / macOS / Ручной Запуск

```bash
# 1. Убедитесь что Docker работает
docker --version
docker-compose --version

# 2. Соберите образ
docker-compose build

# 3. Запустите контейнер
docker-compose up -d

# 4. Проверьте статус
docker-compose ps

# 5. Откройте браузер
# http://localhost:8501
```

## 📦 Детали Docker Образа

### Базовый Образ
- **Python:** 3.13.7-slim
- **ОС:** Debian 12 (Bookworm)
- **Архитектура:** Multi-stage build для оптимизации размера

### Размер Образа
- **Builder stage:** ~1.8GB (временный)
- **Final image:** ~1.2GB
- **Compressed:** ~450MB

### Установленные Пакеты

Все зависимости из `requirements.txt`:

**Core:**
- pandas 2.0.0+
- numpy 1.24.0+
- scikit-learn 1.3.0+

**ML Models:**
- xgboost 2.0.0+
- tensorflow 2.15.0+

**Visualization:**
- streamlit 1.30.0+
- plotly 5.18.0+
- folium 0.15.0+

**Data Processing:**
- pyarrow 14.0.0+
- fastparquet 2023.10.0+

## 🛠️ Управление Контейнером

### Основные Команды

#### Запуск
```bash
# Запуск в фоне (daemon mode)
docker-compose up -d

# Запуск с выводом логов
docker-compose up

# Запуск с пересборкой
docker-compose up -d --build
```

#### Остановка
```bash
# Остановить контейнер
docker-compose stop

# Остановить и удалить контейнер
docker-compose down

# Остановить и удалить с volumes
docker-compose down -v
```

#### Перезапуск
```bash
# Быстрый перезапуск
docker-compose restart

# Перезапуск с пересборкой
docker-compose down
docker-compose up -d --build
```

#### Просмотр Логов
```bash
# Все логи (follow mode)
docker-compose logs -f

# Последние 100 строк
docker-compose logs --tail 100

# Логи с временными метками
docker-compose logs -f --timestamps

# Только ошибки
docker-compose logs -f | grep ERROR
```

### Проверка Статуса

```bash
# Список запущенных контейнеров
docker ps

# Все контейнеры (включая остановленные)
docker ps -a

# Статус Grid Guardian
docker-compose ps

# Детальная информация
docker inspect grid-guardian-app
```

### Мониторинг Ресурсов

```bash
# Реалтайм мониторинг CPU/Memory
docker stats grid-guardian-app

# Однократный снимок
docker stats --no-stream grid-guardian-app

# Использование диска
docker system df
```

## 🔧 Конфигурация

### Переменные Окружения

Редактировать в `docker-compose.yml`:

```yaml
environment:
  # Порт приложения
  - STREAMLIT_SERVER_PORT=8501

  # Адрес сервера (0.0.0.0 = все интерфейсы)
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0

  # Режим headless (без GUI)
  - STREAMLIT_SERVER_HEADLESS=true

  # Отключить телеметрию
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

  # Тема интерфейса
  - STREAMLIT_THEME_BASE=dark
  - STREAMLIT_THEME_PRIMARY_COLOR=#FF4B4B

  # Часовой пояс
  - TZ=Europe/Moscow
```

### Изменение Порта

В `docker-compose.yml`:
```yaml
ports:
  - "8080:8501"  # Внешний:Внутренний
```

После изменения:
```bash
docker-compose down
docker-compose up -d
```

Доступ: http://localhost:8080

### Volume Mounts (Монтирование Данных)

Текущая конфигурация:
```yaml
volumes:
  # Данные (только чтение)
  - ./data:/app/data:ro

  # Логи (чтение-запись)
  - ./logs:/app/logs

  # Модели (чтение-запись)
  - ./models:/app/models
```

**Преимущества:**
- ✅ Данные остаются после удаления контейнера
- ✅ Можно обновлять данные без пересборки
- ✅ Логи доступны на хосте

### Ограничение Ресурсов

В `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # Максимум 2 ядра
      memory: 2G     # Максимум 2GB RAM
    reservations:
      cpus: '1'      # Минимум 1 ядро
      memory: 512M   # Минимум 512MB RAM
```

## 🩺 Health Checks (Проверки Здоровья)

### Автоматические Проверки

Контейнер включает автоматический health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3
```

**Параметры:**
- `interval`: Проверка каждые 30 секунд
- `timeout`: Таймаут запроса 10 секунд
- `start-period`: Ожидание запуска 40 секунд
- `retries`: 3 попытки до признания unhealthy

### Проверка Статуса

```bash
# Статус здоровья
docker inspect --format='{{.State.Health.Status}}' grid-guardian-app

# Полная информация о health check
docker inspect grid-guardian-app | grep -A 10 Health
```

**Возможные статусы:**
- `starting` - Контейнер запускается (первые 40 сек)
- `healthy` - Всё работает ✅
- `unhealthy` - Есть проблемы ❌

### Ручная Проверка

```bash
# Проверка эндпоинта здоровья
curl http://localhost:8501/_stcore/health

# Ожидаемый ответ: {"status":"ok"}
```

## 🐛 Устранение Неполадок

### Порт Занят

**Ошибка:**
```
Bind for 0.0.0.0:8501 failed: port is already allocated
```

**Решение Windows:**
```batch
# Найти процесс на порту 8501
netstat -ano | findstr :8501

# Убить процесс (замените <PID> на номер процесса)
taskkill /PID <PID> /F

# Или изменить порт в docker-compose.yml
```

**Решение Linux/Mac:**
```bash
# Найти и убить процесс
lsof -ti:8501 | xargs kill -9

# Или изменить порт
```

### Контейнер Не Запускается

```bash
# 1. Просмотр детальных логов
docker logs grid-guardian-app

# 2. Проверка ошибок сборки
docker-compose build --no-cache

# 3. Очистка и пересборка
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

### Приложение Падает

```bash
# Последние 200 строк логов
docker logs --tail 200 grid-guardian-app

# Поиск ошибок
docker logs grid-guardian-app 2>&1 | grep -i error

# Перезапуск
docker restart grid-guardian-app

# Если не помогает - полная пересборка
docker-compose down
docker rmi grid-guardian:latest
docker-compose up --build -d
```

### Нехватка Памяти (OOM)

**Симптомы:**
- Контейнер постоянно перезапускается
- В логах: "Killed" или "Out of memory"

**Решение:**

1. Увеличить лимит в `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Было 2G
```

2. Увеличить память в Docker Desktop:
   - Settings → Resources → Memory
   - Рекомендуется 4GB+

3. Перезапустить:
```bash
docker-compose down
docker-compose up -d
```

### Данные Не Загружаются

```bash
# 1. Проверить наличие файлов данных
docker exec grid-guardian-app ls -lh /app/data/raw/

# 2. Проверить доступность данных
docker exec grid-guardian-app python -c "import pandas as pd; print(pd.read_parquet('/app/data/raw/grid_telemetry_data.parquet').shape)"

# 3. Проверить права доступа
docker exec grid-guardian-app stat /app/data/raw/grid_telemetry_data.parquet

# 4. Пересоздать данные на хосте
python data/generate_data.py
```

### Ошибки Импорта Модулей

```bash
# 1. Проверить установленные пакеты
docker exec grid-guardian-app pip list

# 2. Переустановить зависимости
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 3. Проверить конкретный модуль
docker exec grid-guardian-app python -c "import streamlit; print(streamlit.__version__)"
```

## 🔐 Безопасность

### Текущие Меры Безопасности

1. ✅ **Non-root User**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

2. ✅ **Read-only Data Volumes**
   ```yaml
   - ./data:/app/data:ro
   ```

3. ✅ **Минимальный Образ** (slim version)

4. ✅ **XSRF Protection**
   ```toml
   enableXsrfProtection = true
   ```

### Рекомендации для Production

#### 1. Использовать Secrets

```yaml
services:
  grid-guardian:
    secrets:
      - db_password
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

#### 2. HTTPS через Reverse Proxy

**nginx config:**
```nginx
server {
    listen 443 ssl;
    server_name grid-guardian.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### 3. Регулярные Обновления

```bash
# Проверка уязвимостей
docker scan grid-guardian:latest

# Обновление базового образа
docker-compose build --pull --no-cache
```

#### 4. Ограничение Сети

```yaml
networks:
  grid-guardian-network:
    driver: bridge
    internal: true  # Запретить внешний доступ
```

## 🚀 Production Deployment

### Docker Compose Production

Создать `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  grid-guardian:
    image: grid-guardian:latest
    container_name: grid-guardian-prod
    restart: always
    ports:
      - "80:8501"
    volumes:
      - ./data:/app/data:ro
      - ./logs:/app/logs
      - ./models:/app/models
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
      - TZ=Europe/Moscow
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Запуск:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Автоматический Перезапуск

```yaml
restart: always  # Всегда перезапускать
restart: unless-stopped  # Пока не остановлен вручную
restart: on-failure  # Только при ошибках
```

### Backup и Restore

**Backup данных:**
```bash
# Создать backup
docker run --rm --volumes-from grid-guardian-app \
  -v $(pwd):/backup \
  busybox tar czf /backup/grid-guardian-backup.tar.gz /app/data

# Restore
docker run --rm --volumes-from grid-guardian-app \
  -v $(pwd):/backup \
  busybox tar xzf /backup/grid-guardian-backup.tar.gz -C /
```

## 📈 Оптимизация Производительности

### 1. Multi-stage Build

Уже реализован в Dockerfile:
```dockerfile
FROM python:3.13.7-slim as builder
# Install dependencies

FROM python:3.13.7-slim
# Copy only runtime files
```

**Преимущества:**
- ✅ Меньший размер образа (~40% экономии)
- ✅ Быстрее deployment
- ✅ Меньше поверхность атаки

### 2. Build Cache

```bash
# Использовать кэш
docker-compose build

# Игнорировать кэш (при проблемах)
docker-compose build --no-cache

# Использовать BuildKit для ускорения
DOCKER_BUILDKIT=1 docker-compose build
```

### 3. Уменьшение Размера Образа

**Текущие оптимизации:**
```dockerfile
# ✅ Slim base image
FROM python:3.13.7-slim

# ✅ Удаление кэша apt
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# ✅ pip без кэша
RUN pip install --no-cache-dir -r requirements.txt

# ✅ .dockerignore
```

### 4. Настройка Streamlit

В `.streamlit/config.toml`:
```toml
[runner]
fastReruns = true

[server]
maxUploadSize = 200

[client]
toolbarMode = "minimal"
```

## 📚 Дополнительные Ресурсы

### Документация
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Streamlit Deployment](https://docs.streamlit.io/deploy)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)

### Полезные Команды

```bash
# Очистка неиспользуемых образов
docker image prune -a

# Очистка всего (осторожно!)
docker system prune -a --volumes

# Список образов
docker images

# Размер образа
docker images grid-guardian:latest --format "{{.Size}}"

# История слоев образа
docker history grid-guardian:latest

# Экспорт образа
docker save grid-guardian:latest | gzip > grid-guardian-image.tar.gz

# Импорт образа
docker load < grid-guardian-image.tar.gz
```

## ✅ Post-Deployment Checklist

После развертывания Grid Guardian в Docker проверьте:

- [ ] Контейнер запущен: `docker ps | grep grid-guardian`
- [ ] Health check: `docker inspect --format='{{.State.Health.Status}}' grid-guardian-app`
- [ ] Приложение доступно: http://localhost:8501
- [ ] Все 5 страниц загружаются:
  - [ ] 🏠 Home (Главная)
  - [ ] 📊 Monitoring (Мониторинг)
  - [ ] 🔮 Predictions (Предсказания)
  - [ ] 💰 Financial (Финансы)
  - [ ] 🗺️ Maps (Карты)
- [ ] Данные загружаются без ошибок
- [ ] Нет ошибок в логах: `docker logs grid-guardian-app | grep -i error`
- [ ] Ресурсы в норме: `docker stats grid-guardian-app --no-stream`
- [ ] Графики отображаются корректно
- [ ] Интерактивные карты работают
- [ ] Русский язык отображается правильно

## 🆘 Поддержка

**Проблемы с Docker:**
- GitHub Issues: https://github.com/yourusername/grid-guardian/issues
- Docker Forum: https://forums.docker.com/

**Вопросы по Grid Guardian:**
- Документация: [README.md](README.md)
- Тесты: [tests/README.md](tests/README.md)

---

**Версия:** 1.0
**Python:** 3.13.7
**Docker:** 20.10+
**Последнее обновление:** Декабрь 2025
