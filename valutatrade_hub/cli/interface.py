import argparse
import shlex

from valutatrade_hub.core import exceptions, usecases
from valutatrade_hub.infra import database, settings
from valutatrade_hub.logging_config import config

db = database.DatabaseManager()

settings = settings.SettingsLoader()


def welcome() -> None:
    """
    Начальное меню 
    """
    print('Добро пожаловать\n')

    print(
        'register --username **** --password ****'
        ' - зарегистрировать пользователя'
    )

    print(
        'login --username **** --password ****'
        ' - авторизоваться как пользователь'
    )

    print('exit - выйти из программы \n')

def menu() -> None:
    """
    Меню для авторизированного пользователя
    """
    print(
        '\nМеню личного кабинета пользователя\n'
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
        'get-rate --from **** --to ****'
        ' - получить курс валют'
    )

    print(
        'show-rates --$currency **** --$top  ****'
        ' - получить список актуальных курсов валют с фильтрацией '
    )

    print(
        'update-rates --$source ****'
        ' - обновить данные из указанного источника'
    )

    print(
        'exit - выйти из личного кабинета пользователя'
    )

    print('\nPS: $ - необязательный модификатор\n')

def run() -> None:
    """
    Единственная точка входа для пользовательских команд
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

    # show-rates
    show_rates_parser = subparsers.add_parser(
        "show-rates",
        help="Показ список актуальных курсов из кеша"
    )

    show_rates_parser.add_argument(
        "--currency",
        type=str,
        required=False,
        help="Валюта фильтрации"
    )

    show_rates_parser.add_argument(
        "--top",
        type=int,
        required=True,
        help="Количество записей в результате"
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
                            case 'get-rate':
                                usecases.get_rate(
                                    args.source,
                                    args.to
                                )
                            case 'show-rates':
                                usecases.show_rates(
                                    args.currency,
                                    args.top
                                )
                            case 'update-rates':
                                usecases.update_rates(
                                    args.source
                                )
                            case 'exit':
                                break
                    print('Вы снова к главном меню')

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
