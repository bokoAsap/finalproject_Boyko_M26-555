import json


class SettingsLoader():
    __instanse = None

    # new потому что делаю в первый раз и нужно было разобраться в простых вещах
    def __new__(cls, *args, **kwargs):
        if cls.__instanse is None:
            cls.__instanse = super().__new__(cls)
        
        return cls.__instanse

    def __init__(self):
        if not hasattr(self, "_config"):
            self._config = {}
            self.reload()
    
    def reload(self):
        config_path = "valutatrade_hub/config.json"
        
        with open(config_path, "r", encoding='utf-8') as file:
            self._config = json.load(file)

    def get(self, key: str, default = None):
        return self._config.get(key, default)
