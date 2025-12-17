@echo off
SETLOCAL EnableDelayedExpansion

REM Grid Guardian - Docker Quick Start Script
REM Python 3.13.7 | Streamlit Dashboard
REM Автоматический запуск приложения в Docker

echo.
echo ═══════════════════════════════════════════════════
echo    Grid Guardian - Docker Quick Start
echo    Python 3.13.7 ^| Streamlit Dashboard
echo ═══════════════════════════════════════════════════
echo.

REM Check if Docker is installed
echo [1/6] Проверка Docker...
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker не установлен!
    echo.
    echo Пожалуйста, установите Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)
echo ✅ Docker найден

REM Check if Docker is running
echo.
echo [2/6] Проверка состояния Docker...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker не запущен!
    echo.
    echo Пожалуйста, запустите Docker Desktop и попробуйте снова.
    echo.
    pause
    exit /b 1
)
echo ✅ Docker работает

REM Check if Docker Compose is available
echo.
echo [3/6] Проверка Docker Compose...
docker-compose version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose недоступен!
    pause
    exit /b 1
)
echo ✅ Docker Compose найден

REM Check if container is already running
docker ps | findstr "grid-guardian-app" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ⚠️  Контейнер уже запущен!
    echo.
    echo Выберите действие:
    echo   1 - Перезапустить контейнер
    echo   2 - Открыть в браузере
    echo   3 - Остановить контейнер
    echo   4 - Выход
    echo.
    set /p choice="Ваш выбор (1-4): "

    if "!choice!"=="1" goto restart
    if "!choice!"=="2" goto open_browser
    if "!choice!"=="3" goto stop
    if "!choice!"=="4" exit /b 0

    echo Неверный выбор.
    pause
    exit /b 1
)

REM Build the image
echo.
echo [4/6] Сборка Docker образа...
echo.
echo ⏳ Это может занять 5-10 минут при первом запуске...
echo    (загрузка Python 3.13.7 + установка зависимостей)
echo.

docker-compose build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Сборка не удалась!
    echo    Проверьте сообщения об ошибках выше.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Сборка успешна!

REM Start the container
echo.
echo [5/6] Запуск контейнера...
echo.

docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Не удалось запустить контейнер!
    echo.
    pause
    exit /b 1
)

echo ✅ Контейнер запущен!

REM Wait for application to be ready
echo.
echo [6/6] Ожидание готовности приложения...
echo.
echo ⏳ Пожалуйста, подождите 30-40 секунд...
echo    (Streamlit инициализируется)
echo.

timeout /t 30 /nobreak >nul

REM Check health
curl -f http://localhost:8501/_stcore/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Приложение готово!
) else (
    echo ⚠️  Приложение все еще запускается...
    echo    Может потребоваться еще 10-20 секунд
)

goto success

:restart
echo.
echo ⏳ Перезапуск контейнера...
docker-compose restart
echo ✅ Контейнер перезапущен!
timeout /t 10 /nobreak >nul
goto open_browser

:stop
echo.
echo ⏳ Остановка контейнера...
docker-compose down
echo ✅ Контейнер остановлен!
echo.
pause
exit /b 0

:success
echo.
echo ═══════════════════════════════════════════════════
echo    Grid Guardian успешно запущен!
echo ═══════════════════════════════════════════════════
echo.
echo    🌐 URL: http://localhost:8501
echo.
echo    📊 Доступные страницы:
echo       • Главная (Dashboard)
echo       • Мониторинг (Real-time data)
echo       • Предсказания (ML Predictions)
echo       • Финансы (ROI Analysis)
echo       • Карты (Geographic view)
echo.
echo    📝 Полезные команды:
echo       • Логи:      docker-compose logs -f
echo       • Стоп:      docker-compose down
echo       • Рестарт:   docker-compose restart
echo       • Статус:    docker ps
echo.
echo    📚 Документация: DOCKER.md
echo.
echo ═══════════════════════════════════════════════════
echo.

:open_browser
echo ⏳ Открываем браузер...
timeout /t 2 /nobreak >nul
start http://localhost:8501

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
