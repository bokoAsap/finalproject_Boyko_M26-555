import json

from models import Portfolio, User, Wallet


def load_data(file_name: str):
    """
    Загружает данные по имени из файла
    """
    with open(f'{file_name}', 'r', encoding='utf8') as file:
        data = json.load(file)
        return data

def save_data(file_name: str, data: list) :
    """
    Сохраняет данные в файл
    """
    with open(f'{file_name}', 'w', encoding='utf-8') as file:
        json.dump(data, file)

def user_to_dict(user: User):
    """
    Преобразование объекта User к словарю
    """
    return {
        'user_id': user.user_id,
        'username': user.username,
        'hashed_password': user.hashed_password,
        'salt': user.salt,
        'registration_date': user.registration_date.isoformat()
    }

def portfolio_to_dict(portfolio: Portfolio):
    """
    Преобразование объекта Portfolio к словарю
    """
    return {
        'user_id': portfolio.user_id,
        'wallets': portfolio.wallets
    }

def load_portfolio(user_id: int):
    """
    Загрузка портфеля и кошельков
    """
    portfolio_data = None

    portfolios = load_data('portfolios')

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
    
    return portfolio

def save_portfolio(portfolio: Portfolio):
    """
    Сохранение портфеля 
    """
    portfolios = load_data('portfolios')

    portfolio_data = {
        'user_id': portfolio.user_id,
        'wallets': {
            currency_code: {'balance': wallet.balance}
            for currency_code, wallet in portfolio.wallets.items()
        }
    }

    for index, saved_portfolio in enumerate(portfolios):
        if saved_portfolio['user_id'] == portfolio.user_id:
            portfolios[index] = portfolio_data
            save_data('portfolios', portfolios)
            return

    raise ValueError('Портфель пользователя не найден')