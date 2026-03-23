"""
Форматирование постов для Telegram
"""

from datetime import datetime
from ai_generator import get_ai_description  # ← НОВОЕ
import logging

logger = logging.getLogger(__name__)


def format_post(app: dict, channel_type: str) -> dict:
    """
    Создаёт текст и данные для поста
    
    Args:
        app: Данные приложения из API
        channel_type: 'games', 'premium', 'media'
    
    Returns:
        {
            'text': str,
            'icon_url': str,
            'app_url': str
        }
    """
    
    # Базовые данные
    name = app['label']
    version = app['ver_name']
    size_mb = round(app['size'] / 1024 / 1024, 1)
    category = app['category']['name']['ru']
    downloads = app.get('downloads', 0)
    
    # Дата добавления
    timestamp = app['time']
    date_str = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
    
    # Ссылка на приложение
    app_url = f"https://appteka.store/app/{app['app_id']}"
    
    # 🤖 AI-ОПИСАНИЕ
    ai_description = get_ai_description(
        app_name=name,
        category=category,
        version=version,
        downloads=downloads,
        channel_type=channel_type
    )
    
    # Хештег
    hashtag = f"#{category.lower().replace(' ', '_')}"
    
    # Формируем пост
    text = f"""🔥 {name}

{ai_description}

✓ Версия: {version}
✓ Размер: {size_mb} МБ
✓ Категория: {category}
✓ Скачиваний: {downloads}
✓ Добавлено: {date_str}

📲 Скачать: {app_url}

{hashtag}
"""
    
    # Для премиум-канала добавляем бейдж
    if channel_type == 'premium':
        text = text.replace(ai_description, f"💎 PREMIUM\n\n{ai_description}")
    
    return {
        'text': text.strip(),
        'icon_url': app.get('icon'),
        'app_url': app_url
    }
