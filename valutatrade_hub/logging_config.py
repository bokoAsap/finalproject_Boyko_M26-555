import logging
from logging.handlers import RotatingFileHandler
from infra import settings

settings = settings.SettingsLoader()
logs_file = settings.get("LOG_FILE")
logs_level = settings.get("LOG_LEVEL")
logs_format = settings.get("LOG_FORMAT")

def config():
    """
    Кофигурация логгера
    """
    logger = logging.getLogger("ValutaTrade")
    logger.setLevel(logs_level)

    handler = RotatingFileHandler(
        logs_file,
        maxBytes = 5 * 2**20,
        backupCount = 2,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        fmt=logs_format,
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger