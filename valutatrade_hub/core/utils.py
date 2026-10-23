import json


def load_data(file_name: str):
    """
    Загружает данные по имени из файла
    """
    with open(f'{file_name}', 'r', encoding='utf8') as file:
        data = json.load(file)
        return data

def save_data(file_name: str, data: list) :
    """
    Сохраняет данные в файл
    """
    with open(f'{file_name}', 'w', encoding='utf-8') as file:
        json.dump(data, file)