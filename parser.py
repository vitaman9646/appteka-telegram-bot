import requests
import time
from typing import List, Dict
from config import APPTEKA_API_URL, FILTER_HOURS, ITEMS_PER_PAGE


class ApptekParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9',
        })
    
    def get_apps(self, page: int = 0, limit: int = ITEMS_PER_PAGE) -> List[Dict]:
        """Получает список приложений из Appteka API"""
        try:
            response = self.session.get(
                APPTEKA_API_URL,
                params={'page': page, 'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 200:
                return data.get('result', {}).get('entries', [])
            else:
                print(f"⚠️ API вернул статус: {data.get('status')}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return []
    
    def filter_new_apps(self, apps: List[Dict], hours: int = FILTER_HOURS) -> List[Dict]:
        """Фильтрует только новые приложения за последние N часов"""
        now = int(time.time())
        threshold = now - (hours * 3600)
        
        return [
            app for app in apps 
            if app.get('time', 0) >= threshold
        ]
    
    def filter_by_category(self, apps: List[Dict], categories: List[int]) -> List[Dict]:
        """Фильтрует по категориям"""
        if not categories or categories == 'all':
            return apps
        
        return [
            app for app in apps
            if app.get('category', {}).get('id') in categories
        ]
    
    def filter_by_keywords(self, apps: List[Dict], keywords: List[str]) -> List[Dict]:
        """Фильтрует по ключевым словам в названии"""
        if not keywords:
            return apps
        
        filtered = []
        for app in apps:
            label = app.get('label', '').lower()
            if any(keyword.lower() in label for keyword in keywords):
                filtered.append(app)
        
        return filtered
    
    def filter_by_downloads(self, apps: List[Dict], min_downloads: int) -> List[Dict]:
        """Фильтрует по минимальному количеству скачиваний"""
        return [
            app for app in apps
            if app.get('downloads', 0) >= min_downloads
        ]
