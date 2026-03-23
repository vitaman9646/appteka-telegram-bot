#!/bin/bash

echo "🚀 Установка Appteka Telegram Bot"
echo "=================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"

# Создание виртуального окружения
echo ""
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация
source venv/bin/activate

# Обновление pip
echo ""
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Установка зависимостей
echo ""
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Создание .env из примера
if [ ! -f .env ]; then
    echo ""
    echo "📝 Создание .env файла..."
    cp .env.example .env
    echo "⚠️ ВАЖНО: Отредактируй .env файл и добавь токены ботов!"
    echo "   nano .env"
else
    echo ""
    echo "✅ .env файл уже существует"
fi

# Проверка подключений
echo ""
echo "🔍 Проверка подключений к Telegram..."
python3 main.py check

echo ""
echo "=================================="
echo "✅ Установка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируй .env файл: nano .env"
echo "2. Создай ботов через @BotFather"
echo "3. Создай каналы и добавь ботов как админов"
echo "4. Запусти тест: python3 main.py test"
echo "5. Запусти бота: python3 main.py"
echo ""
echo "Для автозапуска добавь в crontab:"
echo "@reboot cd $(pwd) && ./venv/bin/python3 main.py >> bot.log 2>&1"
echo ""
