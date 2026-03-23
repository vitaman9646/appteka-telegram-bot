"""
AI-генератор описаний для приложений через OpenRouter
"""

import os
from openai import OpenAI
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AIGenerator:
    def __init__(self):
        api_key = os.getenv('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')
        if not api_key:
            raise ValueError("❌ Не найден OPENROUTER_API_KEY в .env")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # Модель (можно менять в .env)
        self.model = os.getenv('AI_MODEL', 'anthropic/claude-3.5-sonnet')
        
        # Температура творчества (0.0-1.0)
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))
        
        logger.info(f"✅ AI инициализирован: {self.model}")
    
    
    def generate_description(
        self, 
        app_name: str, 
        category: str,
        version: str,
        downloads: int,
        channel_type: str  # 'games', 'premium', 'media'
    ) -> Optional[str]:
        """
        Генерирует описание приложения
        
        Args:
            app_name: Название приложения
            category: Категория
            version: Версия
            downloads: Количество скачиваний
            channel_type: Тип канала (для стиля описания)
        
        Returns:
            Описание или None при ошибке
        """
        
        # Промпты под каждый канал
        prompts = {
            'games': f"""
Ты — маркетолог Telegram-канала с MOD играми для Android.

Задача: написать короткое (2-3 предложения) продающее описание для игры.

Информация:
- Название: {app_name}
- Категория: {category}
- Версия: {version}
- Популярность: {downloads} скачиваний

Требования:
✓ Упомяни ключевые фичи MOD-версии (unlocked, unlimited, premium)
✓ Создай ажиотаж, но без спама
✓ Используй эмодзи (но не перебарщивай — макс 2-3)
✓ БЕЗ хештегов
✓ НЕ упоминай версию/размер (это уже есть в посте)
✓ Тон: энергичный, но не детский

Пример стиля:
"Легендарная песочница теперь без ограничений! Бесконечные ресурсы, все скины разблокированы и никакой рекламы."

Напиши описание:
""",
            
            'premium': f"""
Ты — маркетолог Telegram-канала с Premium приложениями.

Задача: написать короткое (2-3 предложения) описание премиум-приложения.

Информация:
- Название: {app_name}
- Категория: {category}
- Версия: {version}

Требования:
✓ Подчеркни, что это Pro/Premium версия
✓ Укажи, что разблокировано
✓ Тон: профессиональный, для аудитории 25+
✓ Эмодзи: минимум (💎 можно)
✓ БЕЗ хештегов

Пример:
"Профессиональный видеоредактор с разблокированными фильтрами 4K и AI-инструментами. Полная версия без подписки."

Напиши описание:
""",
            
            'media': f"""
Ты — маркетолог канала с MOD медиа-приложениями (музыка/видео).

Задача: написать 2-3 предложения о приложении.

Информация:
- Название: {app_name}
- Категория: {category}
- Версия: {version}

Требования:
✓ Упомяни фичи: без рекламы, оффлайн-режим, HD-качество
✓ Тон: молодёжный, энергичный
✓ Эмодзи: 2-3 штуки
✓ БЕЗ хештегов

Пример:
"Стриминг музыки без рекламы и с оффлайн-загрузкой 🎵 Весь каталог открыт, качество до 320 kbps!"

Напиши описание:
"""
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompts.get(channel_type, prompts['games'])
                    }
                ],
                temperature=self.temperature,
                max_tokens=150  # ~2-3 предложения
            )
            
            description = response.choices[0].message.content.strip()
            logger.info(f"✅ AI описание создано для {app_name}")
            return description
            
        except Exception as e:
            logger.error(f"❌ Ошибка AI генерации: {e}")
            return None


# Fallback-описания (если AI не сработал)
FALLBACK_DESCRIPTIONS = {
    'games': "🎮 MOD-версия с разблокированными возможностями!",
    'premium': "💎 Премиум-функции доступны без подписки.",
    'media': "🎵 Без рекламы, с оффлайн-режимом!"
}


def get_ai_description(app_name: str, category: str, version: str, downloads: int, channel_type: str) -> str:
    """
    Обёртка с fallback
    """
    try:
        generator = AIGenerator()
        description = generator.generate_description(
            app_name, category, version, downloads, channel_type
        )
        return description or FALLBACK_DESCRIPTIONS[channel_type]
    except Exception as e:
        logger.error(f"❌ AI недоступен: {e}")
        return FALLBACK_DESCRIPTIONS[channel_type]
