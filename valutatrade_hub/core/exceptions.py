class InsufficientFundsError(Exception):
    """
    Представляет собой  ошибку недостатка стредств
    """
    def __init__(self, 
                available: float, 
                required: float, 
                code: str
        ):
        """
        Конструктор класса InsufficientFundsError - 
        кастомного исключения
        """
        super().__init__()
        self.available = available
        self.required = required
        self.code = code

    def __str__(self):
        """
        Строковое представления ошибки InsufficientFundsError
        """
        av = self.available
        req = self.required
        code = self.code
        return f"Недостаточно средств: доступно {av} {code}, требуется {req} {code}"

class CurrencyNotFoundError(Exception):
    """
    Представляет собой  ошибку неизвестная валюта
    """
    def __init__(self, 
                code: str):
        """
        Конструктор класса CurrencyNotFoundError - 
        кастомного исключения
        """
        super().__init__()
        self.code = code
    
    def __str__(self):
        """
        Строковое представления ошибки CurrencyNotFoundError
        """
        return f"Неизвестная валюта '{self.code}'"

class ApiRequestError(Exception):
    """
    Представляет собой  ошибку сбой внешнего API
    """
    def __init__(self, 
                reason: str):
        """
        Конструктор класса ApiRequestError - 
        кастомного исключения
        """
        super().__init__()
        self.reason = reason
    
    def __str__(self):
         """
        Строковое представления ошибки ApiRequestError
        """
        return f"Ошибка при обращении к внешнему API: {self.reason}"
