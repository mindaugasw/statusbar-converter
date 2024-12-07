from abc import ABC, abstractmethod

from src.DTO.ConvertResult import ConvertResult


class ConverterInterface(ABC):
    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def tryConvert(self, text: str) -> (bool, ConvertResult | None):
        """
        @return: (True, ConvertResult) if conversion happened. (False, None) otherwise
        """
        pass