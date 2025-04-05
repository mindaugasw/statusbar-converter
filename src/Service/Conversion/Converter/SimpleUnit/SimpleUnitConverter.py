from typing import Tuple

from src.DTO.ConvertResult import ConvertResult
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Conversion.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.UnitParser import UnitParser
from src.Service.Conversion.UnitToConverterMap import UnitToConverterMap


class SimpleUnitConverter(ConverterInterface):
    """
    Convert simple units, where a single number is followed by a single unit, e.g.: 50 km/h
    """

    _unitParser: UnitParser
    _thousandsDetector: ThousandsDetector
    _unitToConverter: UnitToConverterMap

    _enabled: bool

    def __init__(
        self,
        unitParser: UnitParser,
        unitToConverter: UnitToConverterMap,
    ):
        self._unitParser = unitParser
        self._unitToConverter = unitToConverter

        self._enabled = len(self._unitToConverter) > 0

    def isEnabled(self) -> bool:
        return self._enabled

    def getName(self) -> str:
        return 'Simple'

    def tryConvert(self, text: str) -> Tuple[bool, ConvertResult | None]:
        parsed = self._unitParser.parseText(text)

        if parsed is None:
            return False, None

        success, result = self._unitToConverter[parsed.unit].tryConvert(parsed.number, parsed.unit)

        if result is None:
            return False, None

        result.converterName = f'{self.getName()}.{result.converterName}'

        return True, result
