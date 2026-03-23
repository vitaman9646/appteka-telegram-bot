"""
Главный файл для запуска бота
"""

import sys
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from dotenv import load_dotenv

from config import CHANNELS
from parser import ApptekaPars
from database import Database
from poster import TelegramPoster
from ai_generator import AIGenerator

# Загрузка .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_configuration():
    """Проверка конфигурации перед запуском"""
    
    print("🔍 Проверка конфигурации...\n")
    
    # Проверка каналов
    print(f"📢 Настроено каналов: {len(CHANNELS)}\n")
    for channel_name, channel_config in CHANNELS.items():
        print(f"  • {channel_name.upper()}")
        print(f"    ID канала: {channel_config['channel_id']}")
        print(f"    Категории: {channel_config.get('categories', 'Все')}")
        print(f"    Ключевые слова: {channel_config.get('keywords', 'Нет')}")
        print()
    
    # Проверка парсера
    try:
        parser = ApptekaPars()
        apps = parser.get_latest_apps(limit=1)
        if apps:
            print("✅ Appteka API доступен")
            print(f"   Последнее приложение: {apps[0]['label']}\n")
        else:
            print("⚠️ API вернул пустой список\n")
    except Exception as e:
        print(f"❌ Ошибка подключения к Appteka: {e}\n")
        sys.exit(1)
    
    # Проверка БД
    try:
        db = Database()
        print(f"✅ База данных инициализирована")
        print(f"   Постов в базе: {db.count_posted_apps()}\n")
    except Exception as e:
        print(f"❌ Ошибка БД: {e}\n")
        sys.exit(1)
    
    # Проверка AI
    try:
        ai = AIGenerator()
        test_desc = ai.generate_description(
            app_name="Test App",
            category="Games",
            version="1.0",
            downloads=10,
            channel_type="games"
        )
        if test_desc:
            print("✅ OpenRouter AI подключен")
            print(f"   Модель: {ai.model}")
            print(f"   Тест: {test_desc[:50]}...\n")
        else:
            print("⚠️ AI работает, но вернул пустой ответ\n")
    except Exception as e:
        print(f"❌ Ошибка AI: {e}\n")
        print("⚠️ Бот продолжит работу с fallback-описаниями\n")
    
    # Проверка Telegram ботов
    for channel_name, channel_config in CHANNELS.items():
        try:
            poster = TelegramPoster(channel_name)
            print(f"✅ Telegram бот для {channel_name} подключен")
        except Exception as e:
            print(f"❌ Ошибка бота {channel_name}: {e}\n")
            sys.exit(1)
    
    print("\n✅ Конфигурация корректна!")


def process_new_apps():
    """
    Основная функция: парсинг + постинг
    """
    logger.info("=" * 50)
    logger.info("🚀 Запуск обработки новых приложений")
    
    try:
        # Инициализация
        parser = ApptekaPars()
        db = Database()
        
        # Получаем свежие приложения
        apps = parser.get_latest_apps(limit=50)
        logger.info(f"📦 Получено приложений: {len(apps)}")
        
        posted_count = 0
        
        # Обрабатываем каждый канал
        for channel_name, channel_config in CHANNELS.items():
            logger.info(f"\n📢 Обработка канала: {channel_name}")
            
            poster = TelegramPoster(channel_name)
            
            # Фильтруем приложения под канал
            filtered_apps = parser.filter_for_channel(apps, channel_config)
            logger.info(f"   Подходящих приложений: {len(filtered_apps)}")
            
            # Постим новые
            for app in filtered_apps:
                app_id = app['app_id']
                
                # Проверяем, не постили ли уже
                if db.is_posted(app_id, channel_name):
                    continue
                
                # Постим
                success = poster.post_app(app)
                
                if success:
                    db.mark_as_posted(app_id, channel_name)
                    posted_count += 1
                    logger.info(f"   ✅ Запощено: {app['label']}")
                    
                    # Пауза между постами (антиспам)
                    time.sleep(5)
                else:
                    logger.error(f"   ❌ Не удалось запостить: {app['label']}")
        
        logger.info(f"\n✅ Обработка завершена. Новых постов: {posted_count}")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)


def test_post():
    """
    Тестовый пост (для проверки)
    """
    print("🧪 Тестовый режим\n")
    
    parser = ApptekaPars()
    apps = parser.get_latest_apps(limit=1)
    
    if not apps:
        print("❌ Не удалось получить приложения")
        return
    
    app = apps[0]
    print(f"📱 Тестовое приложение: {app['label']}\n")
    
    # Постим в первый канал
    first_channel = list(CHANNELS.keys())[0]
    print(f"📢 Канал: {first_channel}\n")
    
    poster = TelegramPoster(first_channel)
    success = poster.post_app(app)
    
    if success:
        print("✅ Тестовый пост успешно отправлен!")
    else:
        print("❌ Ошибка отправки")


def main():
    """
    Точка входа
    """
    
    # Проверка аргументов
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'check':
            check_configuration()
            return
        
        elif command == 'test':
            test_post()
            return
        
        elif command == 'once':
            process_new_apps()
            return
        
        else:
            print("❌ Неизвестная команда")
            print("\nДоступные команды:")
            print("  python main.py check  - проверка конфигурации")
            print("  python main.py test   - тестовый пост")
            print("  python main.py once   - одна проверка новых приложений")
            print("  python main.py        - запуск по расписанию")
            return
    
    # Запуск по расписанию
    print("⏰ Запуск планировщика...\n")
    check_configuration()
    
    scheduler = BlockingScheduler()
    
    # Каждые 30 минут
    scheduler.add_job(
        process_new_apps,
        CronTrigger(minute='*/30'),
        id='parse_and_post',
        name='Парсинг и постинг новых приложений',
        replace_existing=True
    )
    
    print(f"\n✅ Бот запущен!")
    print(f"⏰ Следующая проверка: {datetime.now().replace(second=0, microsecond=0)}")
    print("📊 Логи сохраняются в bot.log")
    print("\nНажмите Ctrl+C для остановки\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Бот остановлен")


if __name__ == '__main__':
    main()
