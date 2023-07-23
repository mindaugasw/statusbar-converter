from abc import ABCMeta, abstractmethod


class ClipboardManager(metaclass=ABCMeta):
    @abstractmethod
    def _checkClipboard(self) -> None:
        pass

    @abstractmethod
    def setClipboardContent(self, content: str) -> None:
        pass
