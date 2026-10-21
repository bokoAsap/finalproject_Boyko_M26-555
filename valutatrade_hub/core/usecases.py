import hashlib
import secrets
from datetime import datetime

import utils
from models import Portfolio, User


def user_to_dict(user: User):
    return {
        'user_id': user.user_id,
        'username': user.username,
        'hashed_password': user.hashed_password,
        'salt': user.salt,
        'registration_date': user.registration_date
    }

def portfolio_to_dict(portfolio: Portfolio):
    return {
        'user_id': portfolio.user_id,
        'wallets': portfolio.wallets
    }

def register(username: str, password: str):
    """
    Назначение: создать нового пользователя.
    Шаги:
    Проверить уникальность username в users.json.
    Сгенерировать user_id (например, автоинкремент).
    Захешировать пароль (делайте односторонний псевдо-хеш 
    (например, hashlib.sha256(password + salt)), соль храните рядом.).
    Сохранить пользователя в users.json.
    Создать пустой портфель (portfolios.json: user_id + пустой словарь кошельков).
    Вернуть сообщение об успехе.
    """

    users = utils.load_data('users')

    if username in users:
        raise ValueError(f'{username} уже зарегистрирован')

    user_id = len(users) + 1

    salt = secrets.token_hex(16)

    hashed_password = hashlib.sha256(
        (password + salt).encode('utf-8')
    ).hexdigest()

    now = datetime.now().isoformat()

    new_user = User(
        user_id=user_id,
        username=username,
        hashed_password=hashed_password,
        salt=salt,
        reg_date=now
    )

    user_to_save = user_to_dict(new_user)
    utils.save_data('users', user_to_save)

    new_portfolio = Portfolio(
        user_id=user_id,
        wallet={}
    )

    portfolio_to_save = portfolio_to_dict(new_portfolio)
    utils.save_data('portfolios', portfolio_to_save)

    print(f'Пользователь {username} успешно создан')

def login(username: str, password:str):
    """
    Назначение: создать нового пользователя.
    Шаги:
    Найти пользователя по username.
    Сравнить хеш пароля.
    """
    users = utils.load_data('users')
    
    user_data = users.get(username)

    if user_data is None:
        raise ValueError('Неверное имя пользователя')
    
    user = User(
        user_id=user_data['user_id'],
        username=user_data['username'],
        hashed_password=user_data['hashed_password'],
        salt=user_data['salt'], 
        reg_date=user_data['reg_date']
    )

    if not user.verify_password(password):
        raise ValueError('Неверное имя пользователя или пароль')
    
    return user
