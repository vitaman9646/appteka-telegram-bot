#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import BOTS, PARSE_INTERVAL_MINUTES, FILTER_HOURS
from parser import ApptekParser
from poster import TelegramPoster
from database import Database


class ApptekaBot:
    def __init__(self):
        self.parser = ApptekParser()
        self.db = Database()
        self.posters = {}
        
        # Инициализация постеров для каждого канала
        for channel_name, config in BOTS.items():
            if config.get('token') and config.get('channel'):
                self.posters[channel_name] = {
                    'poster': TelegramPoster(
                        bot_token=config['token'],
                        channel_id=config['channel'],
                        channel_name=channel_name
                    ),
                    'config': config
                }
    
    async def test_all_connections(self):
        """Тестирует подключение ко всем ботам и каналам"""
        print("\n🔍 Проверка подключений...\n")
        
        all_ok = True
        for channel_name, data in self.posters.items():
            ok = await data['poster'].test_connection()
            if not ok:
                all_ok = False
        
        if all_ok:
            print("\n✅ Все подключения работают!\n")
        else:
            print("\n⚠️ Есть проблемы с подключениями. Проверь .env файл\n")
        
        return all_ok
    
    async def process_apps(self):
        """Основной процесс: парсинг + фильтрация + постинг"""
        print(f"\n{'='*60}")
        print(f"🚀 Запуск парсинга: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Получаем приложения
        print("📡 Получаем список приложений...")
        apps = self.parser.get_apps(page=0)
        
        if not apps:
            print("⚠️ Не удалось получить приложения")
            return
        
        print(f"✅ Получено: {len(apps)} приложений")
        
        # Фильтруем новые
        new_apps = self.parser.filter_new_apps(apps, hours=FILTER_HOURS)
        print(f"🆕 Новых за {FILTER_HOURS}ч: {len(new_apps)}")
        
        if not new_apps:
            print("ℹ️ Нет новых приложений для публикации")
            return
        
        # Обрабатываем каждый канал
        for channel_name, data in self.posters.items():
            poster = data['poster']
            config = data['config']
            
            print(f"\n📢 Обработка канала: {channel_name}")
            
            # Фильтруем по настройкам канала
            filtered_apps = new_apps.copy()
            
            # Фильтр по категориям
            if config.get('categories') != 'all':
                filtered_apps = self.parser.filter_by_category(
                    filtered_apps,
                    config.get('categories', [])
                )
            
            # Фильтр по ключевым словам (для премиум-канала)
            if config.get('keywords'):
                filtered_apps = self.parser.filter_by_keywords(
                    filtered_apps,
                    config.get('keywords', [])
                )
            
            # Фильтр по минимальным скачиваниям
            min_downloads = config.get('min_downloads', 0)
            if min_downloads > 0:
                filtered_apps = self.parser.filter_by_downloads(
                    filtered_apps,
                    min_downloads
                )
            
            print(f"   После фильтрации: {len(filtered_apps)} приложений")
            
            # Постим
            posted_count = 0
            is_premium = channel_name == 'premium'
            
            for app in filtered_apps:
                success = await poster.post_app(app, is_premium=is_premium)
                if success:
                    posted_count += 1
                    # Задержка между постами (чтобы не флудить)
                    await asyncio.sleep(3)
            
            print(f"   ✅ Запостили: {posted_count} приложений")
        
        # Статистика
        print(f"\n📊 Всего в базе запощено: {self.db.get_posted_count()} приложений")
        
        # Очистка старых записей (раз в день)
        if datetime.now().hour == 3:  # В 3 ночи
            deleted = self.db.cleanup_old(days=30)
            print(f"🗑️ Очищено старых записей: {deleted}")
        
        print(f"\n{'='*60}")
        print(f"✅ Парсинг завершён: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
    
    def run_once(self):
        """Запуск один раз (для тестирования)"""
        asyncio.run(self.process_apps())
    
    def run_scheduler(self):
        """Запуск по расписанию"""
        print(f"\n🤖 Бот запущен!")
        print(f"⏰ Интервал парсинга: каждые {PARSE_INTERVAL_MINUTES} минут")
        print(f"🕒 Фильтр новых приложений: {FILTER_HOURS} часов")
        print(f"📢 Активных каналов: {len(self.posters)}\n")
        
        # Тестируем подключения
        asyncio.run(self.test_all_connections())
        
        # Первый запуск сразу
        print("🚀 Первый запуск через 10 секунд...\n")
        time.sleep(10)
        asyncio.run(self.process_apps())
        
        # Настраиваем планировщик
        scheduler = BlockingScheduler()
        scheduler.add_job(
            lambda: asyncio.run(self.process_apps()),
            trigger=IntervalTrigger(minutes=PARSE_INTERVAL_MINUTES),
            id='parse_and_post',
            name='Парсинг и постинг приложений',
            replace_existing=True
        )
        
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n👋 Бот остановлен")
            scheduler.shutdown()


if __name__ == '__main__':
    import sys
    
    bot = ApptekaBot()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            print("🧪 Режим тестирования (один запуск)")
            bot.run_once()
        elif sys.argv[1] == 'check':
            print("🔍 Проверка подключений")
            asyncio.run(bot.test_all_connections())
        else:
            print("Использование:")
            print("  python main.py          # Запуск по расписанию")
            print("  python main.py test     # Один запуск (тест)")
            print("  python main.py check    # Проверка подключений")
    else:
        # Обычный запуск по расписанию
        bot.run_scheduler()
