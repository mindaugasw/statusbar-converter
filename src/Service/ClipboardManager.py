from abc import ABCMeta, abstractmethod

import src.events as events
from src.Service.Logger import Logger


class ClipboardManager(metaclass=ABCMeta):
    MAX_CONTENT_LENGTH = 100
    MAX_CONTENT_LENGTH_TRIMMED = 25

    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def initializeClipboardWatch(self) -> None:
        pass

    @abstractmethod
    def setClipboardContent(self, content: str) -> None:
        pass

    def _handleChangedClipboard(self, content: str) -> None:
        # Avoid parsing huge texts to not impact performance
        if len(content) > ClipboardManager.MAX_CONTENT_LENGTH:
            self._logger.logDebug('Too long clipboard content, skipping')
            events.clipboardChanged(None)

            return

        trimmed = content.strip()

        if len(trimmed) > ClipboardManager.MAX_CONTENT_LENGTH_TRIMMED:
            self._logger.logDebug('Too long clipboard content after trimming, skipping')
            events.clipboardChanged(None)

            return

        events.clipboardChanged(trimmed)
