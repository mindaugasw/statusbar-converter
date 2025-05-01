from abc import ABC, abstractmethod


class FormatableExceptionInterface(ABC):
    @abstractmethod
    def formatExceptionData(self) -> str:
        pass
