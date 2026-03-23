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

load_dotenv()

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


def init_database():
    """
    ХОЛОДНЫЙ СТАРТ: Заполнение БД без постинга
    Помечает все существующие приложения как "обработанные"
    """
    print("🗄️ ХОЛОДНЫЙ СТАРТ: Инициализация базы данных\n")
    print("⚠️ Это нужно сделать ОДИН РАЗ перед первым запуском\n")
    
    parser = ApptekaPars()
    db = Database()
    
    # Получаем ВСЕ приложения (максимум что отдаёт API)
    print("📥 Загрузка приложений из Appteka...")
    all_apps = parser.get_latest_apps(limit=1000)
    print(f"✅ Получено: {len(all_apps)} приложений\n")
    
    added_count = 0
    
    # Помечаем все приложения для всех каналов
    for channel_name in CHANNELS.keys():
        print(f"📝 Обработка канала: {channel_name}")
        
        for app in all_apps:
            app_id = app['app_id']
            
            # Проверяем, нет ли уже в БД
            if not db.is_posted(app_id, channel_name):
                db.mark_as_posted(app_id, channel_name)
                added_count += 1
        
        print(f"   ✅ Добавлено записей: {added_count}\n")
        added_count = 0
    
    total = db.count_posted_apps()
    print(f"✅ Инициализация завершена!")
    print(f"📊 Всего записей в БД: {total}")
    print(f"\n💡 Теперь можно:")
    print(f"   1. python main.py fill 30  — залить 30 постов для старта")
    print(f"   2. python main.py          — запустить постоянную работу")


def fill_archive(posts_per_channel=10):
    """
    ПОСТЕПЕННЫЙ СТАРТ: Постинг старых приложений
    
    Args:
        posts_per_channel: Сколько старых постов залить в каждый канал
    """
    print(f"📚 ПОСТЕПЕННОЕ НАПОЛНЕНИЕ: {posts_per_channel} постов на канал\n")
    
    parser = ApptekaPars()
    db = Database()
    
    # Получаем архив
    print("📥 Загрузка приложений...")
    apps = parser.get_latest_apps(limit=500)
    print(f"✅ Загружено: {len(apps)} приложений\n")
    
    total_posted = 0
    
    for channel_name, channel_config in CHANNELS.items():
        print(f"📢 Канал: {channel_name.upper()}")
        
        poster = TelegramPoster(channel_name)
        filtered_apps = parser.filter_for_channel(apps, channel_config)
        
        print(f"   Подходящих приложений: {len(filtered_apps)}")
        
        posted = 0
        
        for app in filtered_apps:
            if posted >= posts_per_channel:
                break
            
            app_id = app['app_id']
            
            # Постим только непощенные
            if not db.is_posted(app_id, channel_name):
                print(f"   📤 Пост {posted + 1}/{posts_per_channel}: {app['label'][:40]}...", end=' ')
                
                success = poster.post_app(app)
                
                if success:
                    db.mark_as_posted(app_id, channel_name)
                    posted += 1
                    total_posted += 1
                    print("✅")
                    time.sleep(8)  # Пауза между постами (антиспам Telegram)
                else:
                    print("❌")
        
        print(f"   📊 Запощено: {posted}/{posts_per_channel}\n")
    
    print(f"✅ Заливка завершена!")
    print(f"📊 Всего запощено: {total_posted} постов")
    print(f"\n💡 Можно:")
    print(f"   • Повторить: python main.py fill {posts_per_channel}")
    print(f"   • Запустить бота: python main.py")


def process_new_apps():
    """
    Основная функция: парсинг + постинг ТОЛЬКО новых
    """
    logger.info("=" * 50)
    logger.info("🚀 Запуск обработки новых приложений")
    
    try:
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
                    
                    # Пауза между постами
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
    print(f"📱 Тестовое приложение: {app['label']}")
    print(f"📦 Категория: {app['category']['name']['ru']}")
    print(f"📊 Скачиваний: {app.get('downloads', 0)}\n")
    
    # Постим в первый канал
    first_channel = list(CHANNELS.keys())[0]
    print(f"📢 Канал: {first_channel}\n")
    
    poster = TelegramPoster(first_channel)
    
    print("📤 Отправка...", end=' ')
    success = poster.post_app(app)
    
    if success:
        print("✅\n")
        print("✅ Тестовый пост успешно отправлен!")
        print("🔍 Проверь канал")
    else:
        print("❌\n")
        print("❌ Ошибка отправки")


def show_stats():
    """
    Показать статистику БД
    """
    print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ\n")
    
    db = Database()
    
    total = db.count_posted_apps()
    print(f"Всего записей: {total}\n")
    
    # Статистика по каналам
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    for channel_name in CHANNELS.keys():
        cursor.execute(
            "SELECT COUNT(*) FROM posted_apps WHERE channel_name = ?",
            (channel_name,)
        )
        count = cursor.fetchone()[0]
        print(f"  {channel_name.upper()}: {count} постов")
    
    conn.close()
    print()


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
        
        elif command == 'init':
            # Холодный старт
            init_database()
            return
        
        elif command == 'fill':
            # Заливка архива
            posts = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            fill_archive(posts_per_channel=posts)
            return
        
        elif command == 'stats':
            # Статистика
            show_stats()
            return
        
        elif command == 'test':
            test_post()
            return
        
        elif command == 'once':
            process_new_apps()
            return
        
        else:
            print("❌ Неизвестная команда\n")
            print("📋 Доступные команды:\n")
            print("  python main.py check       - проверка конфигурации")
            print("  python main.py init        - холодный старт (заполнить БД без постинга)")
            print("  python main.py fill [N]    - залить N старых постов на канал (по умолчанию 10)")
            print("  python main.py stats       - статистика БД")
            print("  python main.py test        - тестовый пост")
            print("  python main.py once        - одна проверка новых приложений")
            print("  python main.py             - запуск по расписанию\n")
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
    
    print(f"\n✅ Бот запущен в режиме PRODUCTION!")
    print(f"⏰ Проверка новых приложений каждые 30 минут")
    print(f"📊 Логи: bot.log")
    print(f"\n💡 Нажми Ctrl+C для остановки\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Бот остановлен")


if __name__ == '__main__':
    main()
