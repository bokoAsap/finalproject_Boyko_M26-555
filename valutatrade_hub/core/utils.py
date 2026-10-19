import json


def load_data(file_name: str):
    """
    Загружает данные по имени из файла
    """
    with open(f'data/{file_name}.json', 'r', encoding='utf8') as file:
        data = json.load(file)
        return data

def save_data(file_name: str, data: list) :
    """
    Сохраняет данные в файл
    """
    with open(f'data/{file_name}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file)