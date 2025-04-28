import threading
from abc import ABC, abstractmethod
from typing import Final

from src.Service.EventService import EventService


class AppLoop(ABC):
    _SLOW_LOOP_INTERVAL: Final = 10

    _events: EventService

    def __init__(self, events: EventService):
        self._events = events

    def startLoop(self) -> None:
        threading.Thread(target=self._processIteration, daemon=True).start()

    @abstractmethod
    def _processIteration(self) -> None:
        pass
