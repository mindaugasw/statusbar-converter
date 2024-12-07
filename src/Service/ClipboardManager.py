from abc import ABC, abstractmethod

import src.events as events
from src.Constant.Logs import Logs
from src.Service.Logger import Logger


class ClipboardManager(ABC):
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

    def _handleChangedClipboard(self, text: str) -> None:
        # Avoid parsing huge texts to not impact performance
        if len(text) > ClipboardManager.MAX_CONTENT_LENGTH:
            self._logger.logDebug(Logs.catClipboard + 'Changed: Too long content, skipping')
            events.clipboardChanged(None)

            return

        trimmed = text.strip()

        if trimmed == '':
            self._logger.logDebug(f'{Logs.catClipboard}Changed to: [empty]')
            events.clipboardChanged(None)

            return

        if len(trimmed) > ClipboardManager.MAX_CONTENT_LENGTH_TRIMMED:
            self._logger.logDebug(Logs.catClipboard + 'Changed: Too long clipboard content after trimming, skipping')
            events.clipboardChanged(None)

            return

        self._logger.logDebug(Logs.catClipboard + 'Changed to: ' + trimmed)
        events.clipboardChanged(trimmed)
