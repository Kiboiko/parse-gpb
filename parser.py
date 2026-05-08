from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

class Parser:
    def __init__(self, headless=True):
        """Инициализация парсера с Selenium"""
        self.headless = headless
        self.driver = self._create_driver()
        self.base_url = 'https://fgis.gost.ru/fundmetrology/cm/results/1-{}'
        
    def _create_driver(self):
        """Создание Chrome драйвера"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        
        # Автоматический скачивание и использование Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        return driver

    def get_vri_data(self, vri_id: int):
        """Получение данных по ID поверки через Selenium"""
        url = self.base_url.format(vri_id)
        
        for attempt in range(3):
            try:
                print(f"  Загружаю страницу (попытка {attempt + 1}/3)...")
                self.driver.get(url)
                
                # Ждем загрузки контента
                wait = WebDriverWait(self.driver, 20)
                
                # Ищем таблицу с данными
                try:
                    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
                except TimeoutException:
                    print(f"  Таймаут при загрузке таблицы для ID {vri_id}")
                    if attempt < 2:
                        time.sleep(random.uniform(2, 4))
                        continue
                    return None
                
                # Получаем все строки таблицы
                rows = self.driver.find_elements(By.TAG_NAME, 'tr')
                
                if not rows:
                    print(f"  На странице не найдено таблиц для ID {vri_id}")
                    return None
                
                # Собираем данные
                data = []
                for row in rows:
                    try:
                        text = row.text.strip()
                        if text and len(text) > 1:
                            data.append(text)
                    except:
                        continue
                
                if not data:
                    print(f"  Не удалось извлечь данные для ID {vri_id}")
                    if attempt < 2:
                        time.sleep(random.uniform(1, 2))
                        continue
                    return None
                
                # Проверяем, что данные содержат ключевые поля
                required_fields = ['Рег. номер', 'Наименование СИ', 'Дата поверки']
                has_required = any(any(field in item for field in required_fields) for item in data)
                
                if not has_required:
                    print(f"  Не найдены обязательные поля для ID {vri_id}")
                    return None
                
                print(f"  Успешно получены данные для ID {vri_id}")
                
                # Задержка для имитации человеческого поведения
                time.sleep(random.uniform(0.5, 1.5))
                
                return data
                
            except TimeoutException:
                print(f"  Таймаут при загрузке {vri_id} (попытка {attempt + 1}/3)")
                if attempt < 2:
                    time.sleep(random.uniform(2, 4))
                    continue
                    
            except WebDriverException as e:
                print(f"  Ошибка WebDriver для {vri_id}: {e}")
                if attempt < 2:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    time.sleep(random.uniform(3, 5))
                    self.driver = self._create_driver()
                    continue
                    
            except Exception as e:
                print(f"  Неожиданная ошибка при обработке {vri_id}: {type(e).__name__}: {e}")
                if attempt < 2:
                    time.sleep(random.uniform(2, 3))
                    continue
        
        return None

    def close(self):
        """Закрытие браузера"""
        try:
            if self.driver:
                self.driver.quit()
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