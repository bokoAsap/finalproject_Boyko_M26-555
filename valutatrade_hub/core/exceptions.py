class InsufficientFundsError(Exception):
    def __init__(self, 
                available: float, 
                required: float, 
                code: str
        ):
        super().__init__()
        self.available = available
        self.required = required
        self.code = code

    def __str__(self):
        av = self.available
        req = self.required
        code = self.code
        return f"Недостаточно средств: доступно {av} {code}, требуется {req} {code}"

class CurrencyNotFoundError(Exception):
    def __init__(self, 
                code: str
        ):
        super().__init__()
        self.code = code
    
    def __str__(self):
        return f"Неизвестная валюта '{self.code}'"

class ApiRequestError(Exception):
    def __init__(self, 
                reason: str
        ):
        super().__init__()
        self.reason = reason
    
    def __str__(self):
        return f"Ошибка при обращении к внешнему API: {self.reason}"
