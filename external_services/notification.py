import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Notification(ABC):
    @abstractmethod
    def notify(self, message: str) -> None:
        pass


class ConsoleNotification(Notification):
    def notify(self, message: str):
        logger.info(message)