import argparse
import shlex

from core import exceptions, usecases


def main():
    """
    Единственной точкой входа для пользовательских команд
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

    while True:
        try:
            command_line = input('>>> ')

            args = parser.parse_args(shlex.split(command_line))

            match args.command:
                case 'register':
                    usecases.register(
                        username=args.username,
                        password=args.password
                    ) 
                case 'login':
                    user = usecases.login(
                        username=args.username,
                        password=args.password
                    )
                case 'show-portfolio':
                    usecases.show_portfolio(
                        user=user,
                        base=args.base
                    )
                case 'buy':
                    usecases.buy(
                        user=user,
                        currency=args.currency,
                        amount=args.amount
                    )
                case 'sell':
                    usecases.sell(
                        user=user,
                        currency=args.currency,
                        amount=args.amount
                    )
                case 'get-rate':
                    usecases.get_rate(
                        source=args.source,
                        to=args.to
                    )
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
