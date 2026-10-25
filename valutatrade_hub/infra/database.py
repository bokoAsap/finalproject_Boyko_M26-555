from core import utils
from infra.settings import SettingsLoader

class DatabaseManager():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        
        return cls.__instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return 
    
        settings = SettingsLoader()

        self.users_path = settings.get("USERS_FILE")
        self.portfolios_path = settings.get("PORTFOLIOS_FILE")
        self.rates_path = settings.get("RATES_FILE")

        self._initialized = True

    def load_user(self):
        return utils.load_data(self.users_path)

    def save_user(self, users):
        return utils.save_data(self.users_path, users)

    def load_rate(self):
        return utils.load_data(self.rates_path)

    def save_rate(self, rates):
        return utils.save_data(self.rates_path, rates)

    def load_portfolio(self):
        return utils.load_data(self.portfolios_path)

    def load_portfolio_by_id(self, user_id):
        return utils.load_portfolio(user_id)

    def save_portfolio(self, portfolios):
        return utils.save_portfolio(portfolios)

    def user_to_dict(self, user):
        return utils.user_to_dict(users)

    def portfolio_to_dict(self, portfolio):
        return utils.portfolio_to_dict(portfolios)
