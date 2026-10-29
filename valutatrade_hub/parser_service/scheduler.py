import time

from valutatrade_hub.parser_service.updater import RatesUpdater


class Scheduler():
    """
    Представляет собой планировщик периодического обновления
    """
    def __init__(
        self,
        updater: RatesUpdater,
        interval: int):
        """
        Конструктор класса Scheduler
        """
        self.updater = updater
        self.interval = interval

    @property   
    def interval(self):
        """
        Геттер атрибута interval
        """
        return self._interval

    @interval.setter
    def interval(self, interval: int):
        """
        Сеттер атрибута interval
        """
        if interval > 0:
            self._interval = interval
        else:
            raise ValueError(
                'Интервал запуска Parser Service '
                'должен быть положительным'
                )
            
    def run(self) -> None:
        """
        Периодически запускает обновление курсов.
        Корректно обрабатывает ошибки и остановку.
        """
        while True:
            try:
                self.updater.run_update()
                
            except Exception:
                pass

            time.sleep(self.interval)
            

    