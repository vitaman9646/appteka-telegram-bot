from datetime import datetime
from typing import Dict
from config import APPTEKA_APP_URL, CATEGORIES


class PostFormatter:
    @staticmethod
    def format_post(app: Dict, include_category: bool = True) -> Dict:
        """
        Форматирует данные приложения для поста в Telegram
        
        Returns:
            {
                'text': str,  # Текст поста
                'photo': str,  # URL иконки
                'app_id': str,
                'package': str,
                'label': str
            }
        """
        # Основные данные
        app_id = app.get('app_id', '')
        label = app.get('label', 'Без названия')
        version = app.get('ver_name', '')
        size_mb = round(app.get('size', 0) / (1024 * 1024), 1)
        downloads = app.get('downloads', 0)
        icon = app.get('icon', '')
        package = app.get('package', '')
        
        # Категория
        category_id = app.get('category', {}).get('id')
        category_name = CATEGORIES.get(category_id, 'Приложения')
        
        # Дата
        timestamp = app.get('time', 0)
        date_str = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
        
        # URL приложения
        app_url = APPTEKA_APP_URL.format(app_id=app_id)
        
        # Формируем текст
        text = f"🔥 {label}\n\n"
        
        # Основная информация
        text += f"✓ Версия: {version}\n"
        text += f"✓ Размер: {size_mb} МБ\n"
        
        if include_category:
            text += f"✓ Категория: {category_name}\n"
        
        text += f"✓ Скачиваний: {downloads}\n"
        text += f"✓ Добавлено: {date_str}\n\n"
        
        # Ссылка
        text += f"📲 Скачать: {app_url}\n\n"
        
        # Хештеги
        hashtag = category_name.lower().replace(' ', '_')
        text += f"#{hashtag}"
        
        return {
            'text': text,
            'photo': icon,
            'app_id': app_id,
            'package': package,
            'label': label
        }
    
    @staticmethod
    def format_premium_post(app: Dict) -> Dict:
        """Специальное форматирование для премиум-приложений"""
        post = PostFormatter.format_post(app, include_category=True)
        
        # Добавляем акцент на премиум
        label = app.get('label', '')
        
        premium_markers = []
        if 'premium' in label.lower():
            premium_markers.append('💎 Premium разблокирован')
        if 'pro' in label.lower():
            premium_markers.append('⭐ Pro версия')
        if 'mod' in label.lower() or 'patched' in label.lower():
            premium_markers.append('🔓 Модификация')
        if 'unlocked' in label.lower():
            premium_markers.append('🔐 Всё открыто')
        
        if premium_markers:
            # Вставляем маркеры после заголовка
            lines = post['text'].split('\n')
            lines.insert(1, '\n'.join(premium_markers))
            post['text'] = '\n'.join(lines)
        
        return post
