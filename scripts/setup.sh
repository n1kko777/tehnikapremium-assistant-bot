#!/bin/bash
# Скрипт установки TehnikaPremium Assistant Bot

set -e

echo "🏠 TehnikaPremium Assistant Bot - Установка"
echo "============================================"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION"

# Создаём виртуальное окружение
echo ""
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip
echo ""
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo ""
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Создаём директории
echo ""
echo "📁 Создание директорий..."
mkdir -p data logs

# Копируем пример конфигурации
if [ ! -f .env ]; then
    echo ""
    echo "⚙️ Создание файла конфигурации..."
    cp env.example .env
    echo "📝 Отредактируйте файл .env и добавьте ваши токены"
fi

echo ""
echo "============================================"
echo "✅ Установка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте .env и добавьте:"
echo "   - TELEGRAM_BOT_TOKEN (от @BotFather)"
echo "   - OPENAI_API_KEY"
echo ""
echo "2. Добавьте демо-товары:"
echo "   python add_demo_products.py"
echo ""
echo "3. Запустите бота:"
echo "   python main.py"
echo "============================================"

