import secrets
from datetime import datetime, timezone

from .currencies import Factory
from .exceptions import ApiRequestError
from .exchange_rates import exchange_rates
from .models import Portfolio, User
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra import database, settings

db = database.DatabaseManager()

settings = settings.SettingsLoader()
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
    users = db.load_user()

    for user in users:
        if user['username'] == username:
            raise ValueError(f'Имя пользователя {username} уже занято') 

    user_id = max(
        (user['user_id'] for user in users),
        default=0
    ) + 1

    salt = secrets.token_hex(16)

    now = datetime.now(timezone.utc)

    new_user = User(
        user_id=user_id,
        username=username,
        hashed_password='',
        salt=salt,
        reg_date=now
    )
     
    new_user.hashed_password = password 

    user_to_save = db.user_to_dict(new_user)
    users.append(user_to_save)

    new_portfolio = Portfolio(
        user_id=user_id,
        wallets={}
    )

    try:
        db.save_portfolio(new_portfolio)
        db.save_user(users)
    except Exception as e:
        raise OSError(
            f'Не удалось создать пользователя. Ошибка: {e}'
        ) from e

    print(
        f'Пользователь {username} зарегистрирован '
        f'(id={new_user.user_id})'
    )
    print(
        f'Войдите: login --username {username} '
        f'--password ****'
    )

    return new_user


@log_action('login')
def login(username: str, password:str):
    """
    Назначение: войти и зафиксировать текущую сессию.
    Шаги:
    Найти пользователя по username.
    Сравнить хеш пароля.
    """

    users = db.load_user()

    user_data = None
    for user in users:
        if user['username'] == username:
            user_data = user
            break

    if user_data is None:
        raise ValueError('Неверное имя пользователя')

    reg_date = datetime.fromisoformat(
        user_data['registration_date']
        )
    
    user = User(
        user_id=user_data['user_id'],
        username=user_data['username'],
        hashed_password=user_data['hashed_password'],
        salt=user_data['salt'], 
        reg_date=reg_date
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
        raise PermissionError(
            'Сначала войдите в аккаунт'
            )
    
    Factory.get_currency(base)
    
    user_id = user.user_id

    portfolio = db.load_portfolio_by_id(user_id)

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
    
    Factory.get_currency(currency)
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError('Сумма должна быть положительным числом')

    portfolio = db.load_portfolio_by_id(user_id)

    if currency not in portfolio.wallets:
        portfolio.add_currency(currency)
    
    wallet = portfolio.get_wallet(currency)

    last_balance = wallet.balance

    wallet.deposit(amount)

    db.save_portfolio(portfolio)

    print(
        f'Покупка выполнена: {amount} {currency} '
    )
        
    print('Изменения в портфеле:')

    print(
        f'- {wallet.currency_code}: '
        f'было {last_balance} → стало {wallet.balance}'
    )

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
    
    Factory.get_currency(currency)
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError('Сумма должна быть положительным числом')
    
    portfolio = db.load_portfolio_by_id(user_id)

    if currency in portfolio.wallets:
        wallet = portfolio.get_wallet(currency)

        last_balance = wallet.balance

        wallet.withdraw(amount)

        db.save_portfolio(portfolio)
        
        print(
            f'Продажа выполнена: {amount} {currency}'
        )
        print('Изменения в портфеле:')
        print(f'- {currency}: '
            f'было {last_balance} → стало {wallet.balance}'
        )

    else:
        raise ValueError(
            f'Такого кошелька в портфеле пользователя {user.username} нет'
        )

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
    Factory.get_currency(source)
    Factory.get_currency(to)
    
    rates = db.load_rate()

    pair = f'{source}_{to}'
    rate = rates.get(pair)

    now = datetime.now()

    course = None
    updated_at = None

    if rate is not None:
        updated_at = datetime.fromisoformat(rate['updated_at'])
        diff = (now - updated_at).total_seconds() 

        if 0 <= diff <= rates_ttl:
            course = rate['rate']
    
    if course is None:
        try:
            course = round(exchange_rates[to] / exchange_rates[source], 2)
        except Exception as e:
            raise ApiRequestError(e)

        updated_at = now
        
        rates[pair] = {
            'rate': course,
            'updated_at': updated_at.isoformat()
        }

        db.save_rate(rates)

    print(
        f'Курс {source}→{to}: '
        f'{course:.2f} (обновлено: '
        f'{updated_at.isoformat()})'
    )
    print(f'Обратный курс {to}→{source}: '
        f'{(1 / course):.2f}'
    )

    return course, updated_at
