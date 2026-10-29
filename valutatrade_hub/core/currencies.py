from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    """
    Представляет собой абстрактный класс валюты
    """
    def __init__(self,
                name: str,
                code: str
        ):
        """
        Конструктор класса Currency
        """
        self.name = name
        self.code = code
    
    @property
    def name(self):
        """
        Геттер атрибута name
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Сеттер атрибута name
        """
        if  not isinstance(name, str):
            raise TypeError('Неправильный тип имени валюты')
        if not name.strip(): 
            raise ValueError('Имя валюты не может быть пустым')
        if not all(word.isalpha() for word in name.split()):
            raise ValueError('Имя валюты может содержать только буквы и пробелы')
    
        self._name = name     
    
    @property
    def code(self):
        """
        Геттер атрибута code
        """
        return self._code
    
    @code.setter
    def code(self, code):
        """
        Сеттер атрибута code
        """
        if isinstance(code, str):
            if (
                code.isalpha() 
                and code.isupper() 
                and 2 <= len(code) <= 5 
                and ' ' not in code):
                self._code = code
            else:
                raise ValueError('Неправильное написание кода валюты')
        else:
            raise TypeError('Неправильный тип кода валюты')
    
    @abstractmethod
    def get_display_info(self) -> str:
        """
        Абстрактный метод для вывода информации о валюте
        """
        return f'{self.code} - {self.name}'
    
class FiatCurrency(Currency):
    """
    Представляет фиатную валюту

    Позволяет получить информацию о валюте
    """
    def __init__(self, 
                name: str,
                code: str,
                issuing_country: str | None = None):
        """
        Конструктор класса FiatCurrency
        """
        super().__init__(name, code)
        self.issuing_country = issuing_country
    
    def get_display_info(self) -> str:
        """
        Возвращает информацию о валюте
        """
        return (
            f'[FIAT] {super().get_display_info()} '
            f'(Issuing: {self.issuing_country})'
        )

class CryptoCurrency(Currency):
    """
    Представляет фиатную валюту

    Позволяет получить информацию о валюте
    """
    def __init__(self,
                name: str,
                code: str,
                algorithm: str | None = None,
                market_cap: float | None = None):
        """
        Конструктор класса CryptoCurrency
        """
        super().__init__(name, code)
        self.algorithm = algorithm 
        self.market_cap = market_cap 

    def get_display_info(self):
        """
        Возвращает информацию о валюте
        """
        return (
            f'[CRYPTO] {super().get_display_info()} '
            f'(Algo: {self.algorithm}, MCAP: {self.market_cap})'
        )

class Factory():
    """
    Класс-фабрика валют
    """
    @staticmethod
    def get_currency(code: str) -> Currency:
        """
        Фабрика создания валют
        """
        fiat = {
            'USD': {
                'name': 'US Dollar',
                'issuing_country': 'United States'
            }, 
            'EUR': {
                'name': 'Euro',
                'issuing_country': 'Eurozone'
            }, 
            'RUB': {
                'name': 'Russian Ruble',
                'issuing_country': 'Russian Federation'
            }, 
            'GBP': {
                'name': 'Pound Sterling',
                'issuing_country': 'United Kingdom'
            }, 
            'CNY': {
                'name': 'Chinese Yuan',
                'issuing_country': 'China'
            }, 
            'JPY': {
                'name': 'Japanese Yen',
                'issuing_country': 'Japan'
            }
        }
        crypto = {
            'BTC': {
                'name': 'Bitcoin',
                'algorithm': 'SHA-256',
                'market_cap': 1.61 * 10**12
            }, 
            'ETH': {
                'name': 'Ethereum',
                'algorithm': 'PoS',
                'market_cap': 203 * 10**9
            }
        }

        currency = None

        if code in fiat.keys():
            currency = FiatCurrency(
                fiat[code]['name'], 
                code,
                fiat[code]['issuing_country']
            )

        elif code in crypto.keys():
            currency = CryptoCurrency(
                crypto[code]['name'], 
                code,
                crypto[code]['algorithm'],
                crypto[code]['market_cap'],
            )

        else:
            raise CurrencyNotFoundError(code=code) from None

        return currency            
    