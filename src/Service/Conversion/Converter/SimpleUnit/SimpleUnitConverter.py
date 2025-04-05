from typing import Tuple

from src.DTO.ConvertResult import ConvertResult
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Conversion.Converter.UnitParser import UnitParser
from src.Service.Conversion.ThousandsDetector import ThousandsDetector


class SimpleUnitConverter(ConverterInterface):
    """
    Convert simple units, where a single number is followed by a single unit, e.g.: 50 km/h
    """

    _unitParser: UnitParser
    _thousandsDetector: ThousandsDetector

    def __init__(
        self,
        unitParser: UnitParser,
    ):
        self._unitParser = unitParser

    def isEnabled(self) -> bool:
        return self._unitParser.isEnabled()

    def getName(self) -> str:
        return 'Simple'

    def tryConvert(self, text: str) -> Tuple[bool, ConvertResult | None]:
        parsed = self._unitParser.parseText(text)

        if parsed is None:
            return False, None

        success, result = parsed.converter.tryConvert(parsed.number, parsed.unit)

        if result is None:
            return False, None

        result.converterName = f'{self.getName()}.{result.converterName}'

        return True, result
