from abc import ABC, abstractmethod

from src.DTO.ConvertResult import ConvertResult


class SimpleConverterInterface(ABC):
    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getUnitIds(self) -> list[str]:
        pass

    @abstractmethod
    def tryConvert(self, number: float, unit: str) -> (bool, ConvertResult | None):
        """
        @return: (True, ConvertResult) if conversion happened. (False, None) otherwise
        """
        pass
