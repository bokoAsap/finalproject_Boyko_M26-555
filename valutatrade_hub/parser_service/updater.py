import logging
from datetime import datetime

from valutatrade_hub.core.exceptions import ApiRequestError

from . import api_clients
from .storage import Storage

logger = logging.getLogger("ValutaTrade")


class RatesUpdater():
    """
    Представляет собой координатор всего процесса обновления: 
    от получение данных от всех клиентов
    до их объединение и сохранение
    """
    def __init__(
        self,
        clients: list[api_clients.BaseApiClient],
        storage: Storage):
        """
        Конструктор класса RatesUpdater 
        """
        self.clients = clients
        self.storage = storage
    
    def run_update(self) -> None:
        """
        Вызывает fetch_rates() у каждого клиента.
        Объединяет полученные словари с курсами в один.
        Добавляет метаданные: source, last_refresh.
        Передает итоговый объект в storage для сохранения.
        Ведет подробное логирование каждого шага 
        (старт, успех/неудача по каждому клиенту, завершение).
        """
        logger.info("Старт обновления курсов валют")

        all_rates = self.storage.load_rates() or {}
        caches = []
        success, fail = 0, 0

        for client in self.clients:
            client_name = type(client).__name__
  
            logger.info(
                "Начало получения курсов от %s",
                client_name
            )
            try:
                rates = client.fetch_rates()
            
            except ApiRequestError as e:
                fail += 1
                logger.error(
                    "Ошибка клиента %s: %s",
                    client_name,
                    e
                )
                continue

            if not rates:
                logger.warning(
                    "Клиент %s вернул пустой ответ",
                    client_name 
                )
                fail += 1
                continue
            
            success += 1

            logger.info(
                "Клиент %s: получено %d курсов",
                client_name,
                len(rates)
            )

            cache = {"pairs": {}}
            for pair, rate in rates.items():
                cache['pairs'][pair] = {
                        "rate": rate["rate"],
                        "updated_at": rate["timestamp"],
                        "source": rate["source"]
                } 

            cache['last_refresh'] = datetime.now().isoformat()
            caches.append(cache)

            all_rates.update(rates)
        
        if success == 0:
            logger.warning(
                "Клиенты не вернули ни одного курса",
            )
            return

        try:
            self.storage.save_rates(all_rates)
            logger.info(
                    "Сохранено %d курсов",
                    len(all_rates),
                )
        
        except Exception as e:
            logger.exception(
                "Ошибка сохранения курсов: %s",
                e
            )
            raise
        
        try:
            self.storage.update_cache(caches)
            logger.info(
                    "Сохранено %d курсов во внутренний кэш",
                    len(all_rates),
                )
        except Exception as e:
            logger.exception(
                "Ошибка сохранения кэша: %s",
                e
            )
            raise
        
        logger.info(
            "Обновления завершено:"
            "успешно: %d, ошибки: %d",
            success,
            fail
            )
