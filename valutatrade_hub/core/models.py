import hashlib


exchange_rates = {
    'USD':
        {
            'RUB': 0.01,
            'EUR': 1.23,
            'GBP': 0.75,
            'CNY': 6.69,
            'JPY': 158,21
        }
}

class User:
    def __init__(self, 
                user_id: int, 
                username: str, 
                hashed_password:str,
                salt: str, 
                reg_date: datetime):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = reg_date
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        if username is not None:
            self._username = username
        else:
            raise ValueError('Имя не может быть пустым')
    
    @property
    def hashed_password(self):
        return self._hashed_password

    @ hashed_password.setter
    def hashed_password(self, password):
        if len(password) > 4:
            self._hashed_password = hashlib.sha256(
                (password + self._salt).encode('utf-8')
                ).hexdigest()
        else:
            raise ValueError('Пароль не может быть короче 4 символов')
    
    @property
    def salt(self):
        return self._salt
    
    @property
    def registration_date(self):
        return self._registration_date

    
    def get_user_info(self):
        """
        Выводит информацию о пользователе (без пароля)
        """
        print(f'ID пользователя: {self.user_id}')
        print(f'Имя пользователя: {self.username}')
        print(f'Соль: {self.salt}')
        print(f'Дата регистрации: {self.registration_date}')

    def change_password(self, new_password: str):
        """
        Изменяет пароль пользователя, с хешированием нового пароля
        """
        self.hashed_password = new_password
    
    def verify_password(self, password: str):
        """
        Проверяет введённый пароль на совпадение
        """
        return self.hashed_password == hashlib.sha256(
                                                    (password + self._salt).encode('utf-8')
                                                    ).hexdigest()  

class Wallet:
    def __init__(self, 
                currency_code: str, 
                balance: float):
        self.currency_code = currency_code
        self._balance = _balance
    
    @property
    def balance(self):
        return self._balance
    
    @balance.setter
    def balance(self, balance):
        if not isinstance(balance, (int, float)):
            raise TypeError('Неподходящий тип данных для баланса кошелька')
        if balance < 0:
            raise ValueError('Баланс не может быть отрицательным')

    def amount_check(amount):
        if amount > 0:
            return amount
        else:
            raise ValueError('Сумма не может быть отрицательной')

    def deposit(self, amount: float):
        """
        Пополнение баланса
        """
        self.balance += amount_check(amount)
    
    def withdraw(self, amount: float):
        """
        Снятие средств (если баланс позволяет)
        """
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise ValueError('Сумма снятия не может быть больше баланса')
    
    def get_balance_info(self):
        """
        Вывод информации о текущем балансе
        """
        print(f'Текущий баланс составляет {self.balance} {self.currency_code}')       

class Portfolio:
    def __init__(self,
        user_id: int,
        wallets: dict[str, Wallet]
    ):
        self._user_id = user_id
        self._wallets = wallets
    
    @property
    def user(self):
        return self._user_id
    
    @property
    def wallets(self):
        return self._wallets

    def add_currency(self, currency_code:str):
        """
        Добавляет новый кошелёк в портфель (если его ещё нет)
        """
        if not currency_code in self.wallets.keys():
            self.wallets[currency_code] == Wallet(currency_code, 0)
        else:
            raise KeyError('Кошелек в такой валюте уже есть в портфеле')
    
    def get_total_value(self, base_currency:str='USD'):
        """
        Возвращает общую стоимость всех валют пользователя 
        в указанной базовой валюте (по курсам, полученным из API или фиктивным данным)
        """
        total_sum = 0
        base_currency_rate = exchange_rates[base_currency]
        for wallet in self.wallets:
            total_sum += wallet['currency_code'] * base_currency_rate['currency_code']
        return total_sum
        
    def get_wallet(currency_code:str):
        """
        Возвращает объект Wallet по коду валюты.
        """
        return self.wallets[currency_code]