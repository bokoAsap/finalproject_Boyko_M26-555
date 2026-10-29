from valutatrade_hub.core import utils

from .settings import SettingsLoader


class DatabaseManager():
    """
    Представляет собой менеджер базы данных
    """    
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Отвечает за создание класса DatabaseManager
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        
        return cls.__instance

    def __init__(self):
        """
        Конструктор класса DatabaseManager
        """
        if getattr(self, '_initialized', False):
            return 
    
        settings = SettingsLoader()

        self.users_path = settings.get("USERS_FILE")
        self.portfolios_path = settings.get("PORTFOLIOS_FILE")
        self.rates_path = settings.get("RATES_FILE")

        self._initialized = True

    def load_user(self):
        """
        Загрузка пользователя
        """
        return utils.load_data(self.users_path)

    def save_user(self, users):
        """
        Схранение пользователя
        """
        return utils.save_data(self.users_path, users)

    def load_rate(self):
        """
        Загрузка курса валюты
        """
        return utils.load_data(self.rates_path)

    def save_rate(self, rates):
        """
        сохранение курса валюты
        """
        return utils.save_data(self.rates_path, rates)

    def load_portfolio(self):
        """
        Загрузка портфеля пользователя
        """
        return utils.load_data(self.portfolios_path)

    def load_portfolio_by_id(self, user_id):
        """
        Загрузка портфеля по id пользователя
        """
        return utils.load_portfolio(
            self.portfolios_path,
            user_id
        )

    def save_portfolio(self, portfolio):
        """
        Сохранение портфеля пользователя
        """
        return utils.save_portfolio(
            self.portfolios_path,
            portfolio
        )

    def user_to_dict(self, users) -> dict:
        """
        Сохранение пользователя как словаря
        """
        return utils.user_to_dict(users)

    def portfolio_to_dict(self, portfolios) -> dict:
        """
        Сохранение портфеля пользователя как словаря
        """
        return utils.portfolio_to_dict(portfolios)
