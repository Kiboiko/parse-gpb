from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from Card import typification
class Parser:
    def __init__(self, headless=False):
        """Настройка браузера при создании объекта класса"""
        options = Options()
        if headless:
            options.add_argument("--headless")  # Без отображения окна
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def get_vri_data(self, vri_id:int):
        """Метод для получения данных по конкретному ID поверки"""
        url = f'https://fgis.gost.ru/fundmetrology/cm/results/1-{str(vri_id)}'
        
        try:
            self.driver.get(url)
            
            # Ждем появления таблицы (тега td)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "td")))
            
            # Собираем все строки таблицы
            rows = self.driver.find_elements(By.TAG_NAME, "tr")
            
            # Собираем данные в список (исключая пустые строки)
            data = [row.text.strip() for row in rows if row.text.strip()]
            return data
            
        except Exception as e:
            print(f"Ошибка при парсинге {vri_id}: {e}")
            return None



    def close(self):
        """Закрытие браузера"""
        self.driver.quit()