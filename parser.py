import requests
from bs4 import BeautifulSoup
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Parser:
    def __init__(self, headless=None):  # headless оставлен для совместимости, но не используется
        """Инициализация парсера на requests"""
        self.session = self._create_session()
        self.base_url = 'https://fgis.gost.ru/fundmetrology/cm/results/1-{}'
        
    def _create_session(self):
        """Создание сессии с повторными попытками и заголовками"""
        session = requests.Session()
        
        # Настройка повторных попыток
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Реалистичные заголовки браузера
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        return session

    def get_vri_data(self, vri_id: int):
        """Получение данных по ID поверки через HTTP запрос"""
        url = self.base_url.format(vri_id)
        
        for attempt in range(3):
            try:
                # Выполняем GET запрос
                response = self.session.get(
                    url, 
                    timeout=30,
                    allow_redirects=True
                )
                
                # Проверяем статус ответа
                response.raise_for_status()
                
                # Проверяем кодировку
                if response.encoding is None:
                    response.encoding = 'utf-8'
                
                # Парсим HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем все строки таблицы
                rows = soup.find_all('tr')
                
                if not rows:
                    print(f"  На странице не найдено таблиц для ID {vri_id}")
                    return None
                
                # Собираем данные, исключая пустые строки
                data = []
                for row in rows:
                    text = row.get_text(strip=True)
                    if text and len(text) > 1:  # Игнорируем слишком короткие строки
                        data.append(text)
                
                # Проверяем, что данные содержат ключевые поля
                required_fields = ['Рег. номер', 'Наименование СИ', 'Дата поверки']
                has_required = any(any(field in item for field in required_fields) for item in data)
                
                if not has_required:
                    print(f"  Не найдены обязательные поля для ID {vri_id}")
                    return None
                
                # Небольшая задержка для имитации человеческого поведения
                time.sleep(random.uniform(0.3, 0.7))
                
                return data
                
            except requests.exceptions.Timeout:
                print(f"  Таймаут при загрузке {vri_id} (попытка {attempt + 1}/3)")
                if attempt < 2:
                    time.sleep(random.uniform(2, 4))
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                print(f"  Ошибка соединения для {vri_id}: {e}")
                if attempt < 2:
                    time.sleep(random.uniform(3, 5))
                    # Возможно, проблема с сессией - создаем новую
                    if attempt == 1:
                        self.session = self._create_session()
                    continue
                    
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    print(f"  Страница не найдена для ID {vri_id} (404)")
                    return None
                elif response.status_code == 403:
                    print(f"  Доступ запрещен для ID {vri_id} (403)")
                    time.sleep(random.uniform(5, 10))
                    if attempt < 2:
                        continue
                else:
                    print(f"  HTTP ошибка {response.status_code} для {vri_id}")
                    
            except Exception as e:
                print(f"  Неожиданная ошибка при обработке {vri_id}: {type(e).__name__}: {e}")
                if attempt < 2:
                    time.sleep(random.uniform(2, 3))
                    continue
            
            return None
        
        return None

    def close(self):
        """Закрытие сессии"""
        try:
            self.session.close()
        except:
            pass


# Версия с кэшированием для ускорения (если нужно обрабатывать повторяющиеся ID)
class CachedParser(Parser):
    def __init__(self, headless=None):
        super().__init__(headless)
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_vri_data(self, vri_id: int):
        """Получение данных с кэшированием"""
        if vri_id in self.cache:
            self.cache_hits += 1
            print(f"  (кэш) ID {vri_id} найден в кэше")
            return self.cache[vri_id]
        
        self.cache_misses += 1
        data = super().get_vri_data(vri_id)
        
        if data:
            self.cache[vri_id] = data
        
        return data
    
    def print_cache_stats(self):
        """Вывод статистики кэша"""
        total = self.cache_hits + self.cache_misses
        if total > 0:
            hit_rate = (self.cache_hits / total) * 100
            print(f"📊 Статистика кэша: попаданий: {self.cache_hits}, промахов: {self.cache_misses}, эффективность: {hit_rate:.1f}%")