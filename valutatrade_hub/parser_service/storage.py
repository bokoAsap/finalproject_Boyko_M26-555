from valutatrade_hub.core.utils import load_data, save_data
from valutatrade_hub.infra.database import DatabaseManager


class Storage():
    """
    Представляет собой обработчик 
    операций чтения/записи
    """
    def __init__(
        self, 
        file_path: str, 
        db: DatabaseManager):
        """
        Конструктор класса Storage
        """
        self.file_path = file_path
        self.db = db

    def load_rates(self) -> dict:
        """
        Загружает данные из хранилища Parser Service
        """
        return load_data(self.file_path) 

    def save_rates(self, rates: dict) -> None:
        """
        Сохраняет данные, полученные от Parser Service, 
        в хранилище 
        """
        save_data(self.file_path, rates)
    
    def update_cache(self, cache: dict) -> None:
        """
        Обновляет локальный кеш с курсами
        """        
        self.db.save_rate(cache)
