@echo off
REM Скрипт установки TehnikaPremium Assistant Bot для Windows

echo ========================================
echo TehnikaPremium Assistant Bot - Установка
echo ========================================

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python не найден. Установите Python 3.10+
    pause
    exit /b 1
)

echo [OK] Python найден

REM Создаём виртуальное окружение
echo.
echo Создание виртуального окружения...
python -m venv venv

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Обновляем pip
echo.
echo Обновление pip...
python -m pip install --upgrade pip

REM Устанавливаем зависимости
echo.
echo Установка зависимостей...
pip install -r requirements.txt

REM Создаём директории
echo.
echo Создание директорий...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Копируем пример конфигурации
if not exist ".env" (
    echo.
    echo Создание файла конфигурации...
    copy env.example .env
    echo Отредактируйте файл .env и добавьте ваши токены
)

echo.
echo ========================================
echo [OK] Установка завершена!
echo.
echo Следующие шаги:
echo 1. Отредактируйте .env и добавьте:
echo    - TELEGRAM_BOT_TOKEN (от @BotFather)
echo    - OPENAI_API_KEY
echo.
echo 2. Добавьте демо-товары:
echo    python add_demo_products.py
echo.
echo 3. Запустите бота:
echo    python main.py
echo ========================================
pause

