import secrets
from datetime import datetime

import utils
from models import Portfolio, User, Wallet


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

def show_portfolio(user: User|None, base: str ='USD'):
    """ Назначение: показать все кошельки и итоговую стоимость в базовой валюте 
    (по умолчанию USD).
    Шаги:
    Убедиться, что пользователь залогинен.
    Загрузить портфель пользователя.
    Если кошельков нет — сообщить об этом.
    Для каждого кошелька: показать currency_code, баланс и посчитать стоимость 
    в base по текущим курсам;
    Показать сумму по всем кошелькам в base.
    """
    if user is None:
        raise PermissionError('Сначала войдите в аккаунт')
    
    user_id = user.user_id

    portfolio_data = None

    portfolios = utils.load_data('portfolios')

    for portfolio in portfolios:
        if portfolio['user_id'] == user_id:
            portfolio_data = portfolio
            break
    
    if portfolio_data is None:
        raise ValueError('Портфель пользователя не найден')
    
    wallets = {}

    for currency_code, wallet_data in portfolio_data['wallets'].items():
        wallets[currency_code] = Wallet(
            currency_code=currency_code,
            balance=wallet_data['balance']
        )

    portfolio = Portfolio(
        user_id=portfolio_data['user_id'],
        wallets=wallets
    )

    print(f'Портфель пользователя {user.username} (база: {base})')

    if not portfolio.wallets:
        print('Кошельков пока нет')
        return
    
    for currency_code, wallet in portfolio.wallets.items():
        wallet.get_balance_info()
        print(f' -> {wallet.count_in_base_currency(base)}')
    
    print('-' * 40)
    total = portfolio.get_total_value(base)
    print(f'ИТОГО: {total} {base}')


def buy(user: User|None, currency:str, amount: float):
    """
    Назначение: купить валюту.
    Шаги:
    Проверить логин.
    Валидировать currency (формат) и amount > 0.
    Если в портфеле нет такого кошелька — автоматически создать 
    (как делает add_currency).
    Увеличить баланс кошелька на amount.
    Опционально (по желанию) вести «расчётную стоимость» покупки для отчёта:
    Получить текущий курс currency → base.
    Посчитать стоимость amount * rate и вывести в итог.
    """
    if user is None:
        raise PermissionError('Сначала войдите в аккаунт')
    
    user_id = user.user_id

    if isinstance(currency, str):
        raise TypeError('Код валюты строка')
    if len(currency) != 3 or not currency.isalpha() or not currency.isupper():
        raise ValueError('Неправильный код валюты')
    
    if amount <= 0:
        raise ValueError('Сумма должны быть положительной')

    portfolio_data = None

    portfolios = utils.load_data('portfolios')

    for portfolio in portfolios:
        if portfolio['user_id'] == user_id:
            portfolio_data = portfolio
            break
    
    if portfolio_data is None:
        raise ValueError('Портфель пользователя не найден')
    
    wallets = {}

    for currency_code, wallet_data in portfolio_data['wallets'].items():
        wallets[currency_code] = Wallet(
            currency_code=currency_code,
            balance=wallet_data['balance']
        )

    portfolio = Portfolio(
        user_id=portfolio_data['user_id'],
        wallets=wallets
    )

    if currency not in portfolio.wallets:
        portfolio.add_currency(currency)
    
    wallet = portfolio.get_wallet(currency)

    last_balance = wallet.balance

    wallet.deposit(amount)

    portfolio_data['wallets'] = {
        currency_code: {'balance': wallet.balance}
        for currency_code, wallet in portfolio.wallets.items()
    }

    utils.save_data('portfolios', portfolios)

    print(f'Покупка выполнена: {amount} {currency} по курсу 59300.00 USD/{currency}')
    print('Изменения в портфеле:')
    print(f'- {wallet.currency_code}: было {last_balance} → стало {wallet.balance}')

def sell(user: User|None, currency:str, amount: float):
    """
    Назначение: продать указанную валюту.
    Шаги:
    Проверить логин.
    Валидировать входные данные.
    Проверить, что кошелёк существует и на нём достаточно средств.
    Уменьшить баланс.
    Опционально: начислить эквивалент в USD (если ведёте кошелёк USD).
    """
    if user is None:
        raise PermissionError('Сначала войдите в аккаунт')
    
    user_id = user.user_id

    if isinstance(currency, str):
        raise TypeError('Код валюты строка')
    if len(currency) != 3 or not currency.isalpha() or not currency.isupper():
        raise ValueError('Неправильный код валюты')
    
    if amount <= 0:
        raise ValueError('Сумма должны быть положительной')
    
    portfolio_data = None

    portfolios = utils.load_data('portfolios')

    for portfolio in portfolios:
        if portfolio['user_id'] == user_id:
            portfolio_data = portfolio
            break
    
    if portfolio_data is None:
        raise ValueError('Портфель пользователя не найден')
    
    wallets = {}

    for currency_code, wallet_data in portfolio_data['wallets'].items():
        wallets[currency_code] = Wallet(
            currency_code=currency_code,
            balance=wallet_data['balance']
        )

    portfolio = Portfolio(
        user_id=portfolio_data['user_id'],
        wallets=wallets
    )

    if currency not in portfolio.wallets:
        portfolio.add_currency(currency)
    
    wallet = portfolio.get_wallet(currency)

    last_balance = wallet.balance

    wallet.withdraw(amount)

    portfolio_data['wallets'] = {
        currency_code: {'balance': wallet.balance}
        for currency_code, wallet in portfolio.wallets.items()
    }

    utils.save_data('portfolios', portfolios)
    
    print(f'Продажа выполнена: {amount} {currency} по курсу 59800.00 USD/{currency}')
    print('Изменения в портфеле:')
    print(f'- {currency}: было {last_balance} → стало {wallet.balance}')

