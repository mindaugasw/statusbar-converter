from abc import ABCMeta, abstractmethod
import src.events as events
from src.Service.Debug import Debug


class ClipboardManager(metaclass=ABCMeta):
    MAX_CONTENT_LENGTH = 100
    MAX_CONTENT_LENGTH_TRIMMED = 25

    _debug: Debug

    def __init__(self, debug: Debug):
        self._debug = debug

    @abstractmethod
    def initializeClipboardWatch(self) -> None:
        pass

    @abstractmethod
    def setClipboardContent(self, content: str) -> None:
        pass

    def _handleChangedClipboard(self, content: str) -> None:
        # Avoid parsing huge texts to not impact performance
        if len(content) > ClipboardManager.MAX_CONTENT_LENGTH:
            self._debug.log('Too long clipboard content, skipping')

            return

        trimmed = content.strip()

        if len(trimmed) > ClipboardManager.MAX_CONTENT_LENGTH_TRIMMED:
            self._debug.log('Too long clipboard content after trimming, skipping')

            return

        events.clipboardChanged(trimmed)
