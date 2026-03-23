import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import Dict
from database import Database
from formatter import PostFormatter


class TelegramPoster:
    def __init__(self, bot_token: str, channel_id: str, channel_name: str):
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.db = Database()
    
    async def post_app(self, app: Dict, is_premium: bool = False) -> bool:
        """
        Постит приложение в канал
        
        Returns:
            True если успешно, False если ошибка
        """
        # Форматируем пост
        if is_premium:
            post_data = PostFormatter.format_premium_post(app)
        else:
            post_data = PostFormatter.format_post(app)
        
        app_id = post_data['app_id']
        
        # Проверяем, не постили ли уже
        if self.db.is_posted(app_id, self.channel_name):
            print(f"⏭️  {post_data['label']} — уже постили в {self.channel_name}")
            return False
        
        # Постим
        try:
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=post_data['photo'],
                caption=post_data['text'],
                parse_mode=None  # Обычный текст без разметки
            )
            
            # Отмечаем как запощенное
            self.db.mark_posted(
                app_id=app_id,
                package=post_data['package'],
                label=post_data['label'],
                channel=self.channel_name
            )
            
            print(f"✅ Запостили в {self.channel_name}: {post_data['label']}")
            return True
            
        except TelegramError as e:
            print(f"❌ Ошибка Telegram при посте в {self.channel_name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Неизвестная ошибка при посте: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Тестирует подключение к боту и каналу"""
        try:
            bot_info = await self.bot.get_me()
            print(f"✅ Бот {self.channel_name}: @{bot_info.username}")
            
            # Проверяем доступ к каналу
            chat = await self.bot.get_chat(self.channel_id)
            print(f"✅ Канал {self.channel_name}: {chat.title}")
            
            return True
        except TelegramError as e:
            print(f"❌ Ошибка подключения {self.channel_name}: {e}")
            return False
