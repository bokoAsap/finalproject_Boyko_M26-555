import argparse
import shlex

from valutatrade_hub.core import exceptions, usecases
from valutatrade_hub.infra import settings, database
from valutatrade_hub.parser_service import config, api_clients, storage, updater

db = database.DatabaseManager()
settings = settings.SettingsLoader()


def welcome() -> None:
    """
    Начальное меню 
    """
    print('Добро пожаловать')

    print(
        'register --username **** --password ****'
        ' - зарегистрировать пользователя'
    )

    print(
        'login --username **** --password ****'
        ' - авторизоваться как пользователь'
    )

    print('exit - выйти из программы')

def menu() -> None:
    """
    Меню для авторизированного пользователя
    """
    print(
        'Меню личного кабинета пользователя'
    )

    print(
        'show-portfolio --$base ***'
        ' - посмотреть свой портфель'
    )

    print(
        'buy --currency **** --amount ****'
        ' - купить валюту'
    )

    print(
        'sell --currency **** --amount ****'
        ' - продать валюту'
    )

    print(
        'show-rates --from **** --to ****'
        ' - получить курс валют'
    )

    print(
        'exit - выйти из личного кабинета пользователя'
    )

    print('PS: $ - необязательный модификатор')

def run() -> None:
    """
    Единственная точка входа для пользовательских команд
    """
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Команда register
    register_parser = subparsers.add_parser(
        "register",
        help="Регистрация пользователя"
    )

    register_parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Имя пользователя"
    )

    register_parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Пароль пользователя"
    )

    # login
    login_parser = subparsers.add_parser(
        "login",
        help="Авторизация пользователя"
    )

    login_parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Имя пользователя"
    )

    login_parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Пароль пользователя"
    )

    # show_portfolio
    show_portfolio_parser = subparsers.add_parser(
        "show-portfolio",
        help="Показ портфеля пользователя"
    )

    show_portfolio_parser.add_argument(
        "--base",
        type=str,
        required=False,
        default=settings.get("DEFAULT_CURRENCY"),
        help="Базовая валюта"
    )

    # buy
    buy_parser = subparsers.add_parser(
        "buy",
        help="Покупка валюты"
    )

    buy_parser.add_argument(
        "--currency",
        type=str,
        required=True,
        help="Код покупаемой валюты"
    )

    buy_parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Количество покупаемой валюты"
    )

    # sell
    sell_parser = subparsers.add_parser(
        "sell",
        help="Покупка валюты"
    )

    sell_parser.add_argument(
        "--currency",
        type=str,
        required=True,
        help="Код продаваемой валюты"
    )

    sell_parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Количество продаваемой валюты"
    )

    # 
    show_rates_parser = subparsers.add_parser(
        "show-rates",
        help="Получение курса текущей валюты к другой"
    )

    show_rates_parser.add_argument(
        "--from",
        dest="source",
        type=str,
        required=True,
        help="Исходная валюта"
    )

    show_rates_parser.add_argument(
        "--to",
        type=str,
        required=True,
        help="Целевая валюта"
    )

    # update-rates
    update_rates_parser = subparsers.add_parser(
        "update-rates",
        help="Запуск немедленного обновления курсов валют"
    )

    update_rates_parser.add_argument(
        "--source",
        type=str,
        required=False,
        help="Обновить данные только из указанного источника"
    )

    subparsers.add_parser(
        "exit", 
        help="Завершение работы"
    )

    user = None

    welcome()
    # Основной цикл программы
    while True:
        try:
            command_line = input('>>> ')

            args = parser.parse_args(shlex.split(command_line))

            match args.command:
                case 'register':
                    usecases.register(
                        args.username,
                        args.password
                    ) 
                case 'login':
                    user = usecases.login(
                        args.username,
                        args.password
                    )
                    menu()
                    while True:
                        command_line = input('>>> ')

                        args = parser.parse_args(shlex.split(command_line))

                        match args.command:
                            case 'show-portfolio':
                                usecases.show_portfolio(
                                    user,
                                    args.base
                                )
                            case 'buy':
                                usecases.buy(
                                    user,
                                    args.currency,
                                    args.amount
                                )
                            case 'sell':
                                usecases.sell(
                                    user,
                                    args.currency,
                                    args.amount
                                )
                            case 'show-rates':
                                usecases.show_rates(
                                    args.source,
                                    args.to
                                )
                            case 'update-rates':
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
                                if args.source == 'coingecko':
                                    selected_clients = [clients[1]]
                                elif args.source == 'exchangerate':
                                    selected_clients = [clients[0]]
                                elif args.source is None:
                                    selected_clients = clients
                                else:
                                    raise ValueError(
                                        f'Неизвестный источник: {args.source}'
                                    )
                                rates_updater = updater.RatesUpdater(
                                        selected_clients, 
                                        app_storage
                                )
    )
                                rates_updater.run()
                            case 'exit':
                                break
                case 'exit':
                    return
                case _:
                    parser.error('Неизвестная команда')
                    return
        # Обработка исключений
        except exceptions.InsufficientFundsError as e:
            print(e)
        except exceptions.CurrencyNotFoundError as e:
            print(e)
            print('Используйте show-rates, чтобы увидеть доступные валюты')
        except exceptions.ApiRequestError as e:
            print(e)
            print('Проверьте подключение или попробуйте позднее')
        except Exception as e:
            print(f'Ошибка: {e}')
        finally:
            user = None
