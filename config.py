import os
from dotenv import load_dotenv

load_dotenv()

# Telegram настройки (3 канала)
BOTS = {
    'games': {
        'token': os.getenv('BOT_TOKEN_GAMES'),
        'channel': os.getenv('CHANNEL_GAMES'),
        'categories': [9],  # Только игры
        'min_downloads': 3,
        'description': 'Игры с модами'
    },
    'premium': {
        'token': os.getenv('BOT_TOKEN_PREMIUM'),
        'channel': os.getenv('CHANNEL_PREMIUM'),
        'categories': 'all',  # Все категории
        'keywords': ['premium', 'pro', 'unlocked', 'mod', 'patched', 'paid', 'full'],
        'min_downloads': 5,
        'description': 'Премиум приложения'
    },
    'media': {
        'token': os.getenv('BOT_TOKEN_MEDIA'),
        'channel': os.getenv('CHANNEL_MEDIA'),
        'categories': [3, 14],  # Медиа + Музыка
        'min_downloads': 5,
        'description': 'Музыка и видео'
    }
}

# Appteka API
APPTEKA_API_URL = "https://appteka.store/api/1/app/list"
APPTEKA_APP_URL = "https://appteka.store/app/{app_id}"

# Парсинг
PARSE_INTERVAL_MINUTES = int(os.getenv('PARSE_INTERVAL_MINUTES', 30))
FILTER_HOURS = int(os.getenv('FILTER_HOURS', 24))
ITEMS_PER_PAGE = 100

# База данных
DATABASE_PATH = 'posted_apps.db'

# AI (опционально)
USE_AI = os.getenv('USE_AI_DESCRIPTIONS', 'false').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Категории Appteka (ID -> название)
CATEGORIES = {
    1: 'Инструменты',
    2: 'Продуктивность',
    3: 'Медиа',
    4: 'Коммуникация',
    5: 'Персонализация',
    6: 'Фото',
    7: 'Социальные',
    8: 'Путешествия',
    9: 'Игры',
    10: 'Образование',
    11: 'Покупки',
    12: 'Здоровье',
    13: 'Финансы',
    14: 'Музыка',
    15: 'Книги'
}
