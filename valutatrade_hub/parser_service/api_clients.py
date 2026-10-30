from abc import ABC, abstractmethod
from datetime import datetime

import requests
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError


class BaseApiClient(ABC):
    """
    Абстрактный класс 
    представляет собой API-клиента
    """
    def __init__(self, url, timeout, ):
        """
        Конструктор класса BaseApiClient
        """
        self.url = url
        self.timeout = timeout
        
    @abstractmethod
    def fetch_rates(self) -> dict:
        """
        Унифицированный интерфейс для получения курсов
        """
        pass


class CoinGeckoClient(BaseApiClient):
    """
    Представляет собой клиента CoinGecko 
    """
    def __init__(
        self, 
        url: str,
        ids: str, 
        vs_currencies: str,
        timeout: int
        ):
        """
        Конструктор класса CoinGeckoClient
        """
        super().__init__(url, timeout)
        self.ids = ids
        self.vs_currencies = vs_currencies

    def fetch_rates(self) -> dict:
        """
        Формирует URL с ids и vs_currencies.
        Отправляет GET-запрос с помощью requests.
        Парсит ответ и приводит его к стандартизированному формату
        Обрабатывает ошибки сети и API, выбрасывая ApiRequestError.
        """
        params = {
            "ids": self.ids,
            "vs_currencies": self.vs_currencies
        }

        try:
            response = requests.get(
                self.url, 
                params=params, 
                timeout=self.timeout
            )

            resp_status = response.status_code
            req_ms = response.elapsed.total_seconds() * 1000
            etag = response.headers.get("ETag")

            if resp_status != 200:
                raise ApiRequestError(
                    f'Код {resp_status}'
                )

            timestamp = datetime.now().isoformat()

            data = response.json()

            rates = {}
            for code, course in data.items():
                if code in ParserConfig.CRYPTO_ID_MAP:
                    source = ParserConfig.CRYPTO_ID_MAP[code]

                    for base, val in course.items():
                        base = base.upper()
                        pair = f"{source}_{base}"

                        rates[pair] = {
                            "id": f'{pair}_{timestamp}',
                            "from_currency": source,
                            "to_currency": base,
                            "rate": val,
                            "timestamp": timestamp,
                            "source": 'CoinGecko',
                            "meta": {
                                "raw_id": code,
                                "request_ms": req_ms,
                                "status_code": resp_status,
                                "etag": etag
                            }
                        } 

            return rates          
        
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(e)        


class ExchangeRateApiClient(BaseApiClient):
    """
    Представляет собой клиента ExchangeRateApi 
    """
    def __init__(
        self, 
        url: str,
        api_key: str, 
        base: str,
        timeout: int
        ):
        """
        Конструктор класса ExchangeRateApiClient
        """
        super().__init__(url, timeout)
        self.api_key = api_key
        self.base = base    
    
    def fetch_rates(self) -> dict:
        """
        Формирует URL, подставляя API-ключ и базовую валюту.
        Парсит ответ, извлекая курсы из вложенного словаря rates.
        Приводит данные к тому же стандартизированному формату.
        Обрабатывает ошибки (неверный ключ, лимит запросов, недоступность).
        """
        url = (
            f"{self.url}/{self.api_key}"
            f"/latest/{self.base}"
        )
        try:
            response = requests.get(
                url,
                timeout=self.timeout
            )
            resp_status = response.status_code
            req_ms = response.elapsed.total_seconds() * 1000
            etag = response.headers.get("ETag")

            if resp_status != 200:
                raise ApiRequestError(
                    f'Код {resp_status}'
                )

            data = response.json()

            if data.get("result") != "success":
                raise ApiRequestError(
                    f'{data.get("result")}'
                )

            rates = {}
            base = data['base_code']
            timestamp = data['time_last_update_utc']
            
            for code, val in data["conversion_rates"].items():
                pair = f"{code}_{base}"
                rates[pair] = {
                    "id": f'{pair}_{timestamp}',
                    "from_currency": code,
                    "to_currency": base,
                    "rate": val,
                    "timestamp": timestamp,
                    "source": 'ExchangeRate-API',
                    "meta": {
                        "raw_id": None,
                        "request_ms": req_ms,
                        "status_code": resp_status,
                        "etag": etag
                    }
                } 

            return rates
        
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(e)  
          