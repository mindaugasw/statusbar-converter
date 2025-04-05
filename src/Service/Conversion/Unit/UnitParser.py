import re
from typing import Final

from src.DTO.Converter.UnitParseResult import UnitParseResult
from src.DTO.Converter.UnitToConverterMap import UnitToConverterMap
from src.Service.Conversion.Unit.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface


class UnitParser:
    _PATTERN: Final = re.compile(r'^([a-z$]+)?(-?[\d,.]*\d[\d,.]*)([a-z/*°\'"`′″.3$]+)?')
    _REGEX_GROUP_UNIT_BEFORE: Final = 1
    _REGEX_GROUP_NUMBER: Final = 2
    _REGEX_GROUP_UNIT_AFTER: Final = 3

    _thousandsDetector: ThousandsDetector
    _unitBeforeToConverter: UnitToConverterMap
    _unitAfterToConverter: UnitToConverterMap

    def __init__(
        self,
        unitBeforeToConverter: UnitToConverterMap,
        unitAfterToConverter: UnitToConverterMap,
        thousandsDetector: ThousandsDetector,
    ):
        self._thousandsDetector = thousandsDetector
        self._unitBeforeToConverter = unitBeforeToConverter
        self._unitAfterToConverter = unitAfterToConverter

    def isEnabled(self) -> bool:
        return len(self._unitBeforeToConverter) > 0 or len(self._unitAfterToConverter) > 0

    def parseText(self, text: str) -> UnitParseResult | None:
        # Remove all whitespace from anywhere in the string
        textSplit = text.split()
        text = ''.join(textSplit).lower()

        # Test if it meets required format and split into groups
        regexResult = re.match(self._PATTERN, text)

        if regexResult is None:
            return None

        # Split into number and unit by regex groups
        unit: str
        unitBefore: str | None = regexResult.group(self._REGEX_GROUP_UNIT_BEFORE)
        unitAfter: str | None = regexResult.group(self._REGEX_GROUP_UNIT_AFTER)

        if (unitBefore is not None) and (unitAfter is not None):
            return None

        converter: UnitConverterInterface

        # Decide if it's unit before/after
        if unitBefore is not None:
            if unitBefore not in self._unitBeforeToConverter:
                return None

            unit = unitBefore
            converter = self._unitBeforeToConverter[unitBefore]
        elif unitAfter is not None:
            if unitAfter not in self._unitAfterToConverter:
                return None

            unit = unitAfter
            converter = self._unitAfterToConverter[unitAfter]
        else:
            return None

        # Parse number
        numberString = regexResult.group(self._REGEX_GROUP_NUMBER)
        number = self._thousandsDetector.parseNumber(numberString)

        if number is None:
            return None

        return UnitParseResult(number, unit, converter)
