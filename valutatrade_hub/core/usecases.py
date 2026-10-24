import secrets
from datetime import datetime, timezone

import utils
from decorator import log_action
from exchange_rates import exchange_rates
from infra import settings
from models import Portfolio, User

settings = settings.SettingsLoader()
users_path = settings.get("USERS_FILE")
portfolios_path = settings.get("PORTFOLIOS_FILE")
rates_path = settings.get("RATES_FILE")
rates_ttl = settings.get("RATES_TTL_SECONDS")
default_currency = settings.get("DEFAULT_CURRENCY")

@log_action('register')
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
    users = utils.load_data(users_path)
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

    user_to_save = utils.user_to_dict(new_user)
    users.append(user_to_save)
    utils.save_data(users_path, users)

    new_portfolio = Portfolio(
        user_id=user_id,
        wallets={}
    )

    portfolios = utils.load_data(portfolios_path)

    portfolio_to_save = utils.portfolio_to_dict(new_portfolio)
    portfolios.append(portfolio_to_save)
    utils.save_data(portfolios_path, portfolios)

    print(f'Пользователь {username} зарегистрирован (id={new_user.user_id})')
    print('Войдите: login --username {username} --password ****')
    return new_user


@log_action('login')
def login(username: str, password:str):
    """
    Назначение: войти и зафиксировать текущую сессию.
    Шаги:
    Найти пользователя по username.
    Сравнить хеш пароля.
    """

    users = utils.load_data(users_path)

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

def show_portfolio(user: User|None, base: str = default_currency):
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

    portfolio = utils.load_portfolio(user_id)

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

@log_action('buy')
def buy(user: User|None, currency:str, amount: float):
    """
    Назначение: купить валюту.
    Шаги:
    Проверить логин.
    Валидировать currency (формат) и amount > 0.
    Если в портфеле нет такого кошелька — автоматически создать 
    (как делает add_currency).
    Увеличить баланс кошелька на amount
    """
    if user is None:
        raise PermissionError('Сначала войдите в аккаунт')
    
    user_id = user.user_id

    if not isinstance(currency, str):
        raise TypeError('Код валюты строка')
    if len(currency) != 3 or not currency.isalpha() or not currency.isupper():
        raise ValueError('Неправильный код валюты')
    
    if amount <= 0:
        raise ValueError('Сумма должны быть положительной')

    portfolio = utils.load_portfolio(user_id)

    if currency not in portfolio.wallets:
        portfolio.add_currency(currency)
    
    wallet = portfolio.get_wallet(currency)

    last_balance = wallet.balance

    wallet.deposit(amount)

    utils.save_portfolio(portfolio)

    print(f'Покупка выполнена: {amount} {currency} по курсу 59300.00 USD/{currency}')
    print('Изменения в портфеле:')
    print(f'- {wallet.currency_code}: было {last_balance} → стало {wallet.balance}')

@log_action('sell')
def sell(user: User|None, currency:str, amount: float):
    """
    Назначение: продать указанную валюту.
    Шаги:
    Проверить логин.
    Валидировать входные данные.
    Проверить, что кошелёк существует и на нём достаточно средств.
    Уменьшить баланс
    """
    if user is None:
        raise PermissionError('Сначала войдите в аккаунт')
    
    user_id = user.user_id

    if not isinstance(currency, str):
        raise TypeError('Код валюты строка')
    if len(currency) != 3 or not currency.isalpha() or not currency.isupper():
        raise ValueError('Неправильный код валюты')
    
    if amount <= 0:
        raise ValueError('Сумма должны быть положительной')
    
    portfolio = utils.load_portfolio(user_id)
    
    wallet = portfolio.get_wallet(currency)

    last_balance = wallet.balance

    wallet.withdraw(amount)

    utils.save_portfolio(portfolio)
    
    print(f'Продажа выполнена: {amount} {currency} по курсу 59800.00 USD/{currency}')
    print('Изменения в портфеле:')
    print(f'- {currency}: было {last_balance} → стало {wallet.balance}')

def get_rate(source:str, to:str):
    """
    Назначение: получить текущий курс одной валюты к другой.
    Шаги:
    Проверить валидность кодов валют (верхний регистр, не пустые).
    Попробовать взять курс из локального кеша rates.json:
    Если курс свежий (например, моложе 5 минут) — показать его.
    Иначе — запросить у Parser Service (или использовать заглушку) → обновить кеш.
    Показать курс и метку времени.
    """
    for currency in [source, to]:
        if not isinstance(currency, str):
            raise TypeError('Код валюты должен быть строкой')
        if len(currency) != 3 or not currency.isalpha() or not currency.isupper():
            raise ValueError('Неправильный код валюты')
    
    rates = utils.load_data('rates')

    pair = f'{source}_{to}'
    rate = rates.get(pair)

    now = datetime.now(timezone.utc)

    course = None
    updated_at = None

    if rate is not None:
        updated_at = datetime.fromisoformat(rate['updated_at'])
        diff = (now - updated_at).total_seconds() 

        if 0 <= diff <= rates_ttl:
            course = rate['rate']
    if course is None:
        course = exchange_rates[source] / exchange_rates[to]

        updated_at = now
        
        rates[pair] = {
            'rate': course,
            'updated_at': updated_at.isoformat()
        }

        utils.save_data('rates', rates)


    print(f'Курс {to}→{source}: {course:.2f} (обновлено: {updated_at.isoformat()})')
    print(f'Обратный курс {source}→{to}: {(1 / course):.2f}')
