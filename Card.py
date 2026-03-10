from typing import TypedDict
from datetime import datetime,date
class Card(TypedDict):
    regNumber:str
    oboznach:str
    name:str
    number:str
    year:int
    modifiction:str
    owner:str
    examinationDate:date
    numberCertificate:str

def typification(s:list)->Card:
    regNumber:str = s[0].split(' ')[-1]
    oboznach:str = s[1].split("СИ ")[1]
    name:str = s[2].split("СИ ")[1]
    number:str = s[3].split("СИ ")[1]
    year:int = int(s[4].split("СИ ")[1])
    modifiction:str = s[5].split("СИ ")[1]
    owner:str = (next((line for line in s if "Владелец СИ" in line), None)).split("СИ ")[1]
    date_str =(next((line for line in s if "Дата поверки СИ" in line), None)).split("СИ ")[1]
    examinationDate:date = datetime.strptime(date_str, "%d.%m.%Y").date()
    numberCertificate:str = (next((line for line in s if "Номер свидетельства" in line), None)).split("Номер свидетельства")[-1].strip()
    
    card = Card = {
        "regNumber":regNumber,
        "oboznach":oboznach,
        "name":name,
        "number":number,
        "year":year,
        "modifiction":modifiction,
        "owner":owner,
        "examinationDate":examinationDate,
        "numberCertificate":numberCertificate
    }
    return card