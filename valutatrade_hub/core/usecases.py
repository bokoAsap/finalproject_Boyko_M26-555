import secrets
from datetime import datetime, timezone

from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra import database, settings
from valutatrade_hub.parser_service import api_clients, config, storage, updater

from .currencies import Factory
from .models import Portfolio, User

db = database.DatabaseManager()

settings = settings.SettingsLoader()
rates_ttl = settings.get("RATES_TTL_SECONDS")
default_currency = settings.get("DEFAULT_CURRENCY")

app_config = config.ParserConfig()

clients = [
    api_clients.ExchangeRateApiClient(
        app_config.EXCHANGERATE_API_URL,
        app_config.EXCHANGERATE_API_KEY,
        app_config.BASE_CURRENCY,
        app_config.REQUEST_TIMEOUT
    ),
    api_clients.CoinGeckoClient(
        app_config.COINGECKO_URL,
        ','.join(list(app_config.CRYPTO_ID_MAP.keys())),
        app_config.BASE_CURRENCY,
        app_config.REQUEST_TIMEOUT
    ),
]

app_storage = storage.Storage(app_config.HISTORY_FILE_PATH, db)

rates_updater = updater.RatesUpdater(
        clients, 
        app_storage
)

@log_action('register')
def register(username: str, password: str) -> User:
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
def login(username: str, password:str) -> User:
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

def show_portfolio(user: User|None, base: str = default_currency) -> None:
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

    rates = db.load_rate()

    portfolio.rates(rates)

    print(f'Портфель пользователя {user.username} (база: {base})')

    if not portfolio.wallets:
        print('Кошельков пока нет')
        return
    
    for currency_code, wallet in portfolio.wallets.items():
        wallet.get_balance_info()
        rate = portfolio.get_rate(currency_code, base)
        print(f' -> {wallet.count_in_base_currency(rate)}')
    
    print('-' * 40)

    total = portfolio.get_total_value(base)
    print(f'ИТОГО: {total} {base}')

@log_action('buy')
def buy(user: User|None, currency:str, amount: float) -> None:
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
def sell(user: User|None, currency:str, amount: float) -> None:
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

def get_rate(source:str, to:str) -> None:
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
    rate = rates["pairs"].get(pair)

    is_reversed = 0
    if rate is None:
        pair = f'{to}_{source}'
        rate = rates["pairs"].get(pair)
        is_reversed = 1

    course = None
    updated_at = None

    now = datetime.now()

    if rate is not None:
        updated_at = datetime.fromisoformat(rate['updated_at'])
        diff = (now - updated_at).total_seconds() 

        if 0 <= diff <= rates_ttl:
            if is_reversed:
                course = 1 / rate['rate']
            else:
                course = rate['rate']
    
    if course is None:
        rates_updater.run_update()
        rates = db.load_rate()
        rate = rates["pairs"].get(pair)

        if rate is None:
            raise ValueError(
                f'Не удалось получить курс {pair}'
            )
    
        course = rate['rate']
        updated_at = datetime.fromisoformat(rate['updated_at'])        

    print(
        f'Курс {source}→{to}: '
        f'{course:.2f} (обновлено: '
        f'{updated_at.isoformat()})'
    )
    print(f'Обратный курс {to}→{source}: '
        f'{(1 / course):.8f}'
    )

def update_rates(source: str = None) -> None:
    """
    Назначение: Запустить немедленное обновление курсов валют
    Шаги:
    Инициализировать RatesUpdater.
    Вызвать его метод run_update().
    Перехватить возможные ApiRequestError и 
    вывести пользователю информативное сообщение.
    Сообщить об успешном завершении и количестве обновленных курсов.
    """
    if source == 'coingecko':
        selected_clients = [clients[1]]
    elif source == 'exchangerate':
        selected_clients = [clients[0]]
    elif source is None:
        selected_clients = clients
    else:
        raise ValueError(
            f'Неизвестный источник: {source}'
        )

    selected_updater = updater.RatesUpdater(
            selected_clients, 
            app_storage
    )
    
    selected_updater.run_update()

def show_rates(
    currency: str = None,
    top: int = None) -> None:
    """
    Назначение: Показать список актуальных курсов 
    из локального кеша с возможностью фильтрации.
    Шаги:
    Прочитать данные из data/rates.json.
    Применить фильтры, если они указаны.
    Отсортировать данные 
    Вывести отформатированную таблицу с курсами 
    и временем их последнего обновления.
    """ 
    dict_rates = db.load_rate()

    rates = dict_rates["pairs"]

    res = rates

    if currency is not None:
        filtered = {
            pair: rate
            for pair, rate in rates.items()
            if currency in pair
        }

        res = filtered
    
    if top is not None:
        sorted_res = dict(
            sorted(
                res.items(), 
                key=lambda item: item[1]['rate'],
                reverse=True
                )
            )

        sliced_res =  dict(list(sorted_res.items())[:top])

        res = sliced_res
    else:
        sorted_res = dict(sorted(res.items()))

        res = sorted_res
    
    print(f'Курс из кеша (updated at {dict_rates["last_refresh"]})')

    for key, val in res.items():
        print(f"- {key}: {val['rate']}")