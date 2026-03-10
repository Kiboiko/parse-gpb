from parser import Parser
from Card import typification
parser = Parser(headless=True)
try:
        results = parser.get_vri_data(482859332)
        print(typification(results))
        # if results:
        #     print("--- Результаты парсинга ---")
        #     for item in results:
        #         print(item)
                
finally:
    parser.close()