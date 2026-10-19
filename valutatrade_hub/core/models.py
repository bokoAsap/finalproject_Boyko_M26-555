import hashlib

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
