import argparse
import shlex
import logging

from valutatrade_hub.core import exceptions, usecases
from valutatrade_hub.infra import settings
from valutatrade_hub.logging_config import config

settings = settings.SettingsLoader()

def welcome():
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

def run():
    """
    Единственной точкой входа для пользовательских команд
    """
    config() 

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

    # get_rate
    get_rate_parser = subparsers.add_parser(
        "get-rate",
        help="Получение курса текущей валюты к другой"
    )

    get_rate_parser.add_argument(
        "--from",
        dest="source",
        type=str,
        required=True,
        help="Исходная валюта"
    )

    get_rate_parser.add_argument(
        "--to",
        type=str,
        required=True,
        help="Целевая валюта"
    )

    subparsers.add_parser(
        "exit", 
        help="Завершение работы"
    )

    user = None

    welcome()
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
                case 'get-rate':
                    usecases.get_rate(
                        args.source,
                        args.to
                    )
                case 'exit':
                    return
                case _:
                    parser.error('Неизвестная команда')
                    return
        except exceptions.InsufficientFundsError as e:
            print(e)
        except exceptions.CurrencyNotFoundError as e:
            print(e)
            print('Используйте get-rate, чтобы увидеть доступные валюты')
        except exceptions.ApiRequestError as e:
            print(e)
            print('Проверьте подключение или попробуйте позднее')
        except Exception as e:
            print(f'Ошибка: {e}')
