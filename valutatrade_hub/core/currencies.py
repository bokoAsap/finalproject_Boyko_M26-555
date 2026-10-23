from abc import ABC, abstractmethod

from exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self,
                name: str,
                code: str
        ):
        self.name = name
        self.code = code
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str):
            if name.isapha() and len(name) != 0:
                self._name = name
            else:
                raise ValueError('Имя не может быть пустым')
        else:
            raise TypeError('Неправильный тип имени')
        
    
    @property
    def code(self):
        return self._code
    
    @code.setter
    def code(self, code):
        if isinstance(code, str):
            if (
                code.isapha() 
                and code.isupper() 
                and 2 <= len(code) <= 5 
                and ' ' not in code):
                self._code = code
            else:
                raise ValueError('Неправильное написание кода валюты')
        else:
            raise TypeError('Неправильный тип кода валюты')
    
    @abstractmethod
    def get_display_info(self):
        return f'{self.code} - {self.name}'
    
class FiatCurrency(Currency):
    def __init__(self, 
                name: str,
                code: str,
                issuing_country: str
    ):
        super().__init__(name, code)
        self.issuing_country = issuing_country
    
    def get_display_info(self):
        return (
            f'[FIAT] {super().get_display_info()} '
            f'(Issuing: {self.issuing_country})'
        )

class CryptoCurrency(Currency):
    def __init__(self,
                name: str,
                code: str,
                algorithm: str,
                market_cap: float 
    ):  
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self):
        return (
            f'[CRYPTO] {super().get_display_info()} '
            f'(Algo: {self.algorithm}, MCAP: {self.market_cap})'
        )

class Factory():
    @staticmethod
    def get_currency(code: str):
        currencies = {
        "USD": FiatCurrency("US Dollar", "USD", "United States"),
        "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
        "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1_000_000),
    }
        try: 
            return currencies[code]
        except KeyError:
            raise CurrencyNotFoundError(code=code) from None
    