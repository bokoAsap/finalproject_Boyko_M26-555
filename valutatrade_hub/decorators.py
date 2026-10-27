import functools
import logging

from valutatrade_hub.core import utils

logger = logging.getLogger("ValutaTrade")

def get_wallet_balance(user, currency):
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


def log_action(action: str, verbose: bool = False):
    action = action.upper()
    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            user = args[0]

            balance_before = None
            balance_after = None
            
            if action in ("REGISTER", "LOGIN"):
                username = user
                currency = None
                amount = None
            else:
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
