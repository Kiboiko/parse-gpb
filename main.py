from parser import Parser
from Card import typification
from ExcelWorker import ExcelWorker
import time
import random
import sys

def main():
    # Настройки
    file_path = r'Сводный Нет в ИС метрология минус 1000-2000.ods'
    start_col = 23
    
    # Можно указать строку начала как аргумент командной строки
    start_row = 867  # Начинаем с места последней ошибки
    if len(sys.argv) > 1:
        try:
            start_row = int(sys.argv[1])
        except:
            pass
    
    print(f"Начинаю обработку со строки: {start_row}")
    
    # Создаем объекты
    parser = Parser(headless=True)
    worker = ExcelWorker(file_path)
    
    try:
        # Получаем все ID из таблицы
        all_ids = worker.get_ids()
        print(f"Найдено ID для обработки: {len(all_ids)}")
        
        # Счетчики для статистики
        success_count = 0
        fail_count = 0
        browser_restart_count = 0
        
        # Обрабатываем каждый ID, начиная с указанной строки
        for i, vri_id in enumerate(all_ids[start_row:], start=start_row):
            print(f"\n[{i+1}/{len(all_ids)}] Обрабатываю ID: {vri_id}")
            
            # Перезапускаем браузер ЧАЩЕ - каждые 50 запросов
            if i > start_row and i % 50 == 0:
                browser_restart_count += 1
                print(f"🔄 Плановый перезапуск браузера #{browser_restart_count}...")
                parser.close()
                time.sleep(5)
                parser = Parser(headless=True)
            
            # Пропускаем пустые значения
            if not vri_id or vri_id == 'nan' or vri_id == '':
                print(f"  Пропускаю пустой ID в строке {i+1}")
                continue
            
            success = False
            # Несколько попыток для каждого ID
            for attempt in range(3):
                try:
                    # Парсим данные с сайта
                    results = parser.get_vri_data(int(vri_id))
                    
                    if results and len(results) > 5:  # Проверяем, что данные есть
                        # Преобразуем в Card и записываем
                        card_data = typification(results)
                        worker.append_card_to_row(card_data, i, start_col)
                        print(f"  ✓ Данные записаны (попытка {attempt + 1})")
                        success = True
                        success_count += 1
                        break
                    else:
                        print(f"  ✗ Нет данных (попытка {attempt + 1})")
                        if attempt < 2:
                            # Увеличиваем паузу перед следующей попыткой
                            time.sleep(random.uniform(3, 5))
                            continue
                    
                except Exception as e:
                    error_str = str(e)
                    print(f"  ✗ Ошибка (попытка {attempt + 1}): {error_str[:100]}")
                    
                    # Если критическая ошибка - перезапускаем браузер
                    if "Unable to allocate" in error_str or "timeout" in error_str.lower() or "stacktrace" in error_str.lower():
                        print("  🔄 Экстренный перезапуск браузера...")
                        parser.close()
                        time.sleep(5)
                        parser = Parser(headless=True)
                        browser_restart_count += 1
                    
                    if attempt < 2:
                        time.sleep(random.uniform(4, 7))
                        continue
                
                # Увеличиваем паузу между попытками
                time.sleep(random.uniform(1, 2))
            
            if not success:
                fail_count += 1
                print(f"  ❌ Пропускаю ID {vri_id} после 3 неудачных попыток")
            
            # Выводим статистику каждые 50 запросов
            if (i + 1) % 50 == 0:
                print(f"\n📊 Статистика: Успешно: {success_count}, Ошибок: {fail_count}, Перезапусков: {browser_restart_count}")
            
            # Увеличенная пауза между разными ID
            time.sleep(random.uniform(2, 3))
        
        print(f"\n✅ Готово! Обработано {len(all_ids[start_row:])} строк")
        print(f"📊 Итоговая статистика: Успешно: {success_count}, Ошибок: {fail_count}, Перезапусков: {browser_restart_count}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        parser.close()
        print("Браузер закрыт")

if __name__ == "__main__":
    main()