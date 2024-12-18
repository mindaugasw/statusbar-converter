from abc import ABC, abstractmethod

from src.DTO.ConvertResult import ConvertResult


class AbstractSimpleConverter(ABC):
    _enabled: bool

    def __init__(self, enabled: bool):
        self._enabled = enabled

    def isEnabled(self) -> bool:
        return self._enabled

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getUnitIds(self) -> list[str]:
        pass

    @abstractmethod
    def tryConvert(self, number: float, unitId: str) -> (bool, ConvertResult | None):
        """
        @param number
        @param unitId Given unitId will always be an existing one for this converter,
            in lowercase, without any whitespace
        @return: (True, ConvertResult) if conversion happened. (False, None) otherwise
        """
        pass
