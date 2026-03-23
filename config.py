import os
from dotenv import load_dotenv

load_dotenv()

# Telegram настройки
BOTS = {
    'main': {
        'token': os.getenv('BOT_TOKEN_MAIN'),
        'channel': os.getenv('CHANNEL_MAIN'),
        'categories': 'all',  # Все категории
        'min_downloads': int(os.getenv('MIN_DOWNLOADS', 5))
    },
    'games': {
        'token': os.getenv('BOT_TOKEN_GAMES'),
        'channel': os.getenv('CHANNEL_GAMES'),
        'categories': [9],  # Games
        'min_downloads': 3
    },
    'tools': {
        'token': os.getenv('BOT_TOKEN_TOOLS'),
        'channel': os.getenv('CHANNEL_TOOLS'),
        'categories': [1, 2, 3, 4],  # Tools, Productivity, etc
        'min_downloads': 3
    },
    'premium': {
        'token': os.getenv('BOT_TOKEN_PREMIUM'),
        'channel': os.getenv('CHANNEL_PREMIUM'),
        'categories': 'all',
        'keywords': ['premium', 'pro', 'unlocked', 'mod', 'patched'],
        'min_downloads': 10
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
