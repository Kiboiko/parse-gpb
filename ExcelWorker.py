import pandas as pd
import ezodf

class ExcelWorker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(self.file_path, engine='odf')

    def get_ids(self):
        """Возвращает список ID, извлеченных из 15-й колонки (индекс 14)"""
        ids = []
        for _, row in self.df.iterrows():
            val = str(row.values[14]).split('/')[-1]
            ids.append(val)
        return ids
    
    def append_card_to_row(self, card: dict, row_index: int, start_col: int = 23):
        """
        Дописывает данные из Card в конкретную строку ODS файла
        """
        # Открываем ODS документ
        doc = ezodf.opendoc(self.file_path)
        sheet = doc.sheets[0]
        
        # Преобразуем Card в список значений
        card_values = [
            str(card.get('regNumber', '')),
            str(card.get('oboznach', '')),
            str(card.get('name', '')),
            str(card.get('number', '')),
            str(card.get('year', '')),
            str(card.get('modifiction', '')),
            str(card.get('owner', '')),
            str(card.get('examinationDate', '')),
            str(card.get('numberCertificate', ''))
        ]
        
        # Записываем значения
        for i, value in enumerate(card_values):
            col = start_col + i
            # Убеждаемся, что ячейка существует
            while sheet.ncols() <= col:
                sheet.append_columns(1)
            while len(sheet) <= row_index:
                sheet.append_rows(1)
            
            sheet[(row_index+1, col)].set_value(value)
        
        doc.save()