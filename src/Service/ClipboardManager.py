from abc import ABC, abstractmethod
from typing import Final

from src.Constant.Logs import Logs
from src.Service.EventService import EventService
from src.Service.Logger import Logger


class ClipboardManager(ABC):
    _MAX_CONTENT_LENGTH: Final[int] = 100
    _MAX_CONTENT_LENGTH_TRIMMED: Final[int] = 25

    _events: EventService
    _logger: Logger

    def __init__(self, events: EventService, logger: Logger):
        self._events = events
        self._logger = logger

    @abstractmethod
    def validateSystem(self) -> bool:
        pass

    @abstractmethod
    def initializeClipboardWatch(self) -> None:
        pass

    @abstractmethod
    def setClipboardContent(self, content: str) -> None:
        pass

    def _handleChangedClipboard(self, text: str) -> None:
        # Avoid parsing huge texts to not impact performance
        if len(text) > ClipboardManager._MAX_CONTENT_LENGTH:
            self._logger.logDebug(Logs.catClipboard + 'Changed: Too long content, skipping')
            self._events.dispatchClipboardChanged(None)

            return

        trimmed = text.strip()

        if trimmed == '':
            self._logger.logDebug(f'{Logs.catClipboard}Changed to: [empty]')
            self._events.dispatchClipboardChanged(None)

            return

        if len(trimmed) > ClipboardManager._MAX_CONTENT_LENGTH_TRIMMED:
            self._logger.logDebug(Logs.catClipboard + 'Changed: Too long clipboard content after trimming, skipping')
            self._events.dispatchClipboardChanged(None)

            return

        self._logger.logDebug(Logs.catClipboard + 'Changed to: ' + trimmed)
        self._events.dispatchClipboardChanged(trimmed)
