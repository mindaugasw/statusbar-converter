from abc import ABC, abstractmethod
from typing import Tuple

from src.DTO.ConvertResult import ConvertResult


class ConverterInterface(ABC):
    @abstractmethod
    def isEnabled(self) -> bool:
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    # TODO does return type really need 2 variables here? Maybe `ConvertResult | None` would be enough?
    @abstractmethod
    def tryConvert(self, text: str) -> Tuple[bool, ConvertResult | None]:
        """
        :param text: text will already have whitespace trimmed around start and end
        :return: (True, ConvertResult) if conversion happened. (False, None) otherwise
        """
        pass
