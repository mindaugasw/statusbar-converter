from abc import ABC, abstractmethod

from src.DTO.ConvertResult import ConvertResult


class ConverterInterface(ABC):
    @abstractmethod
    def isEnabled(self) -> bool:
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def tryConvert(self, text: str) -> (bool, ConvertResult | None):
        """
        @param: text will already have whitespace trimmed around start and end

        @return: (True, ConvertResult) if conversion happened. (False, None) otherwise
        """
        pass
