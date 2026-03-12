from parser import Parser
from Card import typification
from ExcelWorker import ExcelWorker
import time

def main():
    # Настройки
    file_path = r'Сводный Нет в ИС метрология минус 1000-2000.ods'
    start_col = 23  # Столбец X (0-based)
    
    # Создаем объекты
    parser = Parser(headless=True)
    worker = ExcelWorker(file_path)
    
    try:
        # Получаем все ID из таблицы
        all_ids = worker.get_ids()
        print(f"Найдено ID для обработки: {len(all_ids)}")
        
        # Обрабатываем каждый ID
        for i, vri_id in enumerate(all_ids):
            print(f"\n[{i+1}/{len(all_ids)}] Обрабатываю ID: {vri_id}")
            
            # Пропускаем пустые значения
            if not vri_id or vri_id == 'nan':
                print(f"Пропускаю пустой ID в строке {i+1}")
                continue
            
            try:
                # Парсим данные с сайта
                results = parser.get_vri_data(int(vri_id))
                
                if results:
                    # Преобразуем в Card и записываем
                    card_data = typification(results)
                    worker.append_card_to_row(card_data, i, start_col)
                    print(f"✓ Данные записаны")
                else:
                    print(f"✗ Не удалось получить данные")
                
                # Небольшая пауза между запросами
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Ошибка: {e}")
                continue
        
        print(f"\nГотово! Обработано {len(all_ids)} строк")
        
    finally:
        parser.close()

if __name__ == "__main__":
    main()