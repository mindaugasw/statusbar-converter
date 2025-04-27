import re
from typing import Final

from src.Constant.UnitPosition import UnitPosition
from src.DTO.Converter.UnitParseResult import UnitParseResult
from src.Service.Conversion.Unit.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Service.Conversion.Unit.UnitToConverterMapper import UnitToConverterMapper


class UnitParser:
    # For debugging pattern see https://regexr.com/8ds6v
    _PATTERN: Final = re.compile(r'^([a-z$]+)?(-?[\d,.]*\d[\d,.]*)([a-z/*°\'"`′″.3$]+)?')
    _REGEX_GROUP_UNIT_BEFORE: Final = 1
    _REGEX_GROUP_NUMBER: Final = 2
    _REGEX_GROUP_UNIT_AFTER: Final = 3

    _thousandsDetector: ThousandsDetector
    _unitToConverterMapper: UnitToConverterMapper

    def __init__(
        self,
        unitToConverterMapper: UnitToConverterMapper,
        thousandsDetector: ThousandsDetector,
    ):
        self._thousandsDetector = thousandsDetector
        self._unitToConverterMapper = unitToConverterMapper

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
            converter = self._unitToConverterMapper.getConverter(unitBefore, UnitPosition.BEFORE)

            if converter is None:
                return None

            unit = unitBefore
        elif unitAfter is not None:
            converter = self._unitToConverterMapper.getConverter(unitAfter, UnitPosition.AFTER)

            if converter is None:
                return None

            unit = unitAfter
        else:
            return None

        # Parse number
        numberString = regexResult.group(self._REGEX_GROUP_NUMBER)
        number = self._thousandsDetector.parseNumber(numberString)

        if number is None:
            return None

        return UnitParseResult(number, unit, converter)
