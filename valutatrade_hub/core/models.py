import hashlib
from datetime import datetime

from .exceptions import InsufficientFundsError


class User:
    """
    Представляет собой пользователя

    Позволяет сменить и проверить пароль пользователя,
    и получить о нем информацию
    """
    def __init__(self, 
                user_id: int, 
                username: str, 
                hashed_password:str,
                salt: str, 
                reg_date: datetime):
        """
        Конструктор класса User
        """
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = reg_date
    
    @property
    def user_id(self):
        """
        Геттер атрибута user_id
        """
        return self._user_id
    
    @property
    def username(self):
        """
        Геттер атрибута username
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Сеттер атрибута username
        """
        if username is not None:
            self._username = username
        else:
            raise ValueError('Имя не может быть пустым')
    
    @property
    def hashed_password(self):
        """
        Геттер атрибута hashed_password
        """
        return self._hashed_password
    
    @property
    def salt(self):
        """
        Геттер атрибута salt
        """
        return self._salt

    @ hashed_password.setter
    def hashed_password(self, password):
        """
        Сеттер атрибута hashed_password
        """
        if len(password) >= 4:
            self._hashed_password = hashlib.sha256(
                (password + self.salt).encode('utf-8')
            ).hexdigest()
        else:
            raise ValueError('Пароль не может быть короче 4 символов')
    
    @property
    def registration_date(self):
        """
        Геттер атрибута registration_date
        """
        return self._registration_date
    
    def get_user_info(self) -> None:
        """
        Выводит информацию о пользователе (без пароля)
        """
        print(f'ID пользователя: {self.user_id}')
        print(f'Имя пользователя: {self.username}')
        print(f'Соль: {self.salt}')
        print(f'Дата регистрации: {self.registration_date}')

    def change_password(self, new_password: str) -> None:
        """
        Изменяет пароль пользователя, с хешированием нового пароля
        """
        self.hashed_password = new_password
    
    def verify_password(self, password: str) -> None:
        """
        Проверяет введённый пароль на совпадение
        """
        return self.hashed_password == hashlib.sha256(
                (password + self._salt).encode('utf-8')
                ).hexdigest()  

class Wallet:
    """
    Представляет сосбой кошелек пользователя 
    в некоторой валюте

    Позволяет пополнять, списывать, получать 
    сумму конкретного кошелька,
    и пересчитать сумму в базовой валюте
    """
    def __init__(self, 
                currency_code: str, 
                balance: float):
        """
        Конструктор класса Wallet
        """
        self.currency_code = currency_code
        self._balance = balance
    
    @property
    def balance(self):
        """
        Геттер атрибута balance
        """
        return self._balance
    
    @balance.setter
    def balance(self, balance):
        """
        Сеттер атрибута balance
        """
        if not isinstance(balance, (int, float)):
            raise TypeError('Неподходящий тип данных для баланса кошелька')

        if balance < 0:
            raise ValueError('Баланс не может быть отрицательным')

        self._balance = balance

    def _amount_check(self, amount) -> float:
        """
        Проверяет поступающий amount на соотвествие типу данных
        и положительность
        """
        if not isinstance(amount, (int, float)):
            raise TypeError('Неподходящий тип данных для суммы')
        
        if amount <= 0:
            raise ValueError('Сумма должна быть положительной')
        
        return amount

    def deposit(self, amount: float) -> None:
        """
        Пополнение баланса
        """
        self.balance += self._amount_check(amount)
    
    def withdraw(self, amount: float) -> None:
        """
        Снятие средств (если баланс позволяет)
        """
        amount = self._amount_check(amount)
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise InsufficientFundsError(
                available=self.balance,
                required=amount,
                code=self.currency_code
            )
    
    def get_balance_info(self) -> None:
        """
        Вывод информации о текущем балансе
        """
        print(f'{self.currency_code}: {self.balance}', end='') 

    def count_in_base_currency(self, rate: float) -> float:
        """
        Пересчет баланса кошелька в базой валюте, по умолчанию в долларах
        """
        balance_in_base_currency = (self.balance * rate)

        return balance_in_base_currency

class Portfolio:
    """
    Представляет сосбой портфель пользователя,
    состоящий из нескольких кошельков

    Позволяет добавить новую валюту в портфель,
    получить сумму активов в некоторой валюте,
    и по коду валюты получить кошелек
    """
    def __init__(self,
        user_id: int,
        wallets: dict[str, Wallet],
        rates: dict = {}):
        """
        Конструктор класса Portfolio
        """
        self._user_id = user_id
        self._wallets = wallets
        self._rates = rates 
    
    @property
    def user_id(self):
        """
        Геттер атрибута user_id
        """
        return self._user_id
    
    @property
    def wallets(self):
        """
        Геттер атрибута wallets
        """
        return self._wallets.copy()

    @property
    def rates(self):
        """
        Геттер атрибута rates
        """
        return self._rates

    @rates.setter
    def rates(self, rates: dict):
        """
        Cеттер атрибута rates
        """
        self._rates = rates.copy()

    def add_currency(self, currency_code:str) -> None:
        """
        Добавляет новый кошелёк в портфель (если его ещё нет)
        """
        if currency_code not in self._wallets:
            self._wallets[currency_code] = Wallet(currency_code, 0)
        else:
            raise KeyError('Кошелек в такой валюте уже есть в портфеле')
    
    def get_rate(
        self, 
        currency: str,
        base: str) -> float:
        """
        Возвращает коэффициент конвертации валюты
        """
        if currency == base:
            rate = 1.0
        else:
            pairs = self._rates['pairs']
            course = (
                pairs.get(f'{currency}_{base}') 
                or pairs.get(f'{base}_{currency}')
            )
            if course is not None:
                if f'{currency}_{base}' in pairs:
                    rate = course['rate']
                else:
                    rate = 1 / course['rate']
            else:
                raise ValueError(
                    f"Курс {currency}_{base} не найден"
                )
        
        return rate
    
    def get_total_value(self, base_currency:str = 'USD') -> float:
        """
        Возвращает общую стоимость всех валют пользователя 
        в указанной базовой валюте (по курсам, полученным из API или фиктивным данным)
        """
        total_sum = 0
        

        for wallet in self._wallets.values():
            currency = wallet.currency_code

            rate = self.get_rate(currency, base_currency)               

            total_sum += wallet.count_in_base_currency(rate)
        
        return total_sum
                
    def get_wallet(self, currency_code:str) -> None:
        """
        Возвращает объект Wallet по коду валюты.
        """
        return self._wallets[currency_code]