import sqlite3
import time
from typing import List, Set
from config import DATABASE_PATH


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Создаёт таблицы при первом запуске"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posted_apps (
                app_id TEXT PRIMARY KEY,
                package TEXT,
                label TEXT,
                channel TEXT,
                posted_at INTEGER
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posted_at 
            ON posted_apps(posted_at)
        ''')
        self.conn.commit()
    
    def is_posted(self, app_id: str, channel: str) -> bool:
        """Проверяет, было ли приложение уже запощено в канал"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT 1 FROM posted_apps WHERE app_id = ? AND channel = ?',
            (app_id, channel)
        )
        return cursor.fetchone() is not None
    
    def mark_posted(self, app_id: str, package: str, label: str, channel: str):
        """Отмечает приложение как запощенное"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO posted_apps 
            (app_id, package, label, channel, posted_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (app_id, package, label, channel, int(time.time())))
        self.conn.commit()
    
    def get_posted_count(self, channel: str = None) -> int:
        """Возвращает количество запощенных приложений"""
        cursor = self.conn.cursor()
        if channel:
            cursor.execute(
                'SELECT COUNT(*) FROM posted_apps WHERE channel = ?',
                (channel,)
            )
        else:
            cursor.execute('SELECT COUNT(*) FROM posted_apps')
        return cursor.fetchone()[0]
    
    def cleanup_old(self, days: int = 30):
        """Удаляет записи старше N дней"""
        threshold = int(time.time()) - (days * 86400)
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM posted_apps WHERE posted_at < ?',
            (threshold,)
        )
        self.conn.commit()
        return cursor.rowcount
