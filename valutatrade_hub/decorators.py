import functools
import logging
from typing import Callable, ParamSpec, TypeVar

from valutatrade_hub.core import utils

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("ValutaTrade")

def get_wallet_balance(user, currency) -> float|None:
    """
    Получение баланса пользователя
    """
    if user is None or currency is None:
        return None

    try:
        portfolio = utils.load_portfolio(user.user_id)

        wallet = portfolio.wallets.get(currency)

        if wallet is None:
            return 0.0
        
        return wallet.balance
    
    except Exception as e:
        logger.info(
            'Не удалось получить баланс кошелька'
            f'Ошибка: {e}'
        )
        return None


def log_action(
    action: str, 
    verbose: bool = False
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Логгирование на уровне INFO следующую структуру:
    timestamp (ISO), action (BUY/SELL/REGISTER/LOGIN),
    username (или user_id),
    currency_code, amount,
    rate и base (если применимо),
    result (OK/ERROR),
    error_type/error_message при исключениях.
    Декоратор пробрасывает исключения дальше и фиксирует их в лог.
    Поддержка опции verbose 
    """
    action = action.upper()
    def decorator(
        func: Callable[P, R]
        ) -> Callable[P, R]:

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> R:

            user = args[0]

            balance_before = None
            balance_after = None
            
            if action in ("REGISTER", "LOGIN"):
                username = user
                currency = None
                amount = None
            else:
                # Лоика логгирования для BUY/SELL
                username = user.username if user is not None else None
                currency = args[1]
                amount = args[2]

                if verbose:
                    balance_before = get_wallet_balance(user, currency)

            try:
                result = func(*args, **kwargs)

                message = f'action = {action} username = '
                result_message = ' result=OK'

                if action in ['REGISTER', 'LOGIN']:
                    logger.info(
                        message + user + result_message
                    )
                else:
                    verbose_message = ''
                    if verbose:
                        balance_after = get_wallet_balance(user, currency)
                        verbose_message = (
                            f'было: {balance_before}, стало: {balance_after} '
                        ) 
                    logger.info(
                        message + 
                        f'{username} currency={currency} amount={amount} ' + 
                        verbose_message + 
                        result_message
                    )

                return result

            # Обработка исключений
            except Exception as e:

                message = f'action = {action} username = '
                error_message = (
                    f' result=ERROR error_type={type(e).__name__}' 
                    f'error_message={str(e)}'
                )

                if action in ['REGISTER', 'LOGIN']:
                    logger.info(
                        message + user + error_message
                    )
                else:
                    logger.info(
                        message + 
                        f'{username} currency={currency} amount={amount} ' +
                        error_message
                    )
                raise
        return wrapper
    return decorator
