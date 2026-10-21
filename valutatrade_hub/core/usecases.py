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
        'registration_date': user.registration_date.isoformat()
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
    for user in users:
        if user['username'] == username:
            raise ValueError(f'Имя пользователя {username} уже занято')
    

    user_id = max(
        (user['user_id'] for user in users),
        default=0
    ) + 1

    salt = secrets.token_hex(16)

    now = datetime.now()

    new_user = User(
        user_id=user_id,
        username=username,
        hashed_password='',
        salt=salt,
        reg_date=now
    )

    new_user.username = username        
    new_user.hashed_password = password 

    user_to_save = user_to_dict(new_user)
    users.append(user_to_save)
    utils.save_data('users', users)

    new_portfolio = Portfolio(
        user_id=user_id,
        wallets={}
    )

    portfolios = utils.load_data('portfolios')

    portfolio_to_save = portfolio_to_dict(new_portfolio)
    portfolios.append(portfolio_to_save)
    utils.save_data('portfolios', portfolios)

    print(f'Пользователь {username} зарегистрирован (id={new_user.user_id})')
    print('Войдите: login --username {username} --password ****')
    return new_user

def login(username: str, password:str):
    """
    Назначение: войти и зафиксировать текущую сессию.
    Шаги:
    Найти пользователя по username.
    Сравнить хеш пароля.
    """
    users = utils.load_data('users')

    for user in users:
        if user['username'] == username:
            user_data = user
            break

    if user_data is None:
        raise ValueError('Неверное имя пользователя')
    
    user = User(
        user_id=user_data['user_id'],
        username=user_data['username'],
        hashed_password=user_data['hashed_password'],
        salt=user_data['salt'], 
        reg_date=user_data['registration_date']
    )

    if not user.verify_password(password):
        raise ValueError('Неверное имя пользователя или пароль')
    
    print(f"Вы вошли как '{username}'")    
    return user
