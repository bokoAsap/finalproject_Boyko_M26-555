import json
from typing import Any


class SettingsLoader():
    """
    Представляет собой единую точку конфигурации

    Позволяет загрузить/кешировать конфигурацию проекта
    """
    __instanse = None

    # new потому что делаю в первый раз и нужно было разобраться в простых вещах
    def __new__(cls, *args, **kwargs):
        """
        Отвечает за создание класса SettingsLoader
        """
        if cls.__instanse is None:
            cls.__instanse = super().__new__(cls)
        
        return cls.__instanse
        
    def __init__(self):
        """
        Конструктор класса SettingsLoader
        """
        if not hasattr(self, "_config"):
            self._config = {}
            self.reload()
    
    def reload(self) -> None:
        """
        Перезагрузка конфигурации
        """
        config_path = "valutatrade_hub/config.json"
        
        with open(config_path, "r", encoding='utf-8') as file:
            self._config = json.load(file)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Загрузка кконфигурации
        """
        return self._config.get(key, default)
