from abc import ABCMeta, abstractmethod
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
