import re
from typing import Final

from src.Constant.UnitGroup import UnitGroup
from src.DTO.Converter.UnitParseResult import UnitParseResult
from src.Service.Conversion.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.UnitToConverterMap import UnitToConverterMap


class UnitParser:
    _PATTERN_IS_NUMBER_AND_TEXT: Final = re.compile(r'^((-)?([\d,.]*\d[\d,.]*))([a-z/*°\'"`′″.3]+)')
    _REGEX_GROUP_UNIT_BEFORE: Final = -1
    _REGEX_GROUP_NUMBER: Final = -1
    _REGEX_GROUP_UNIT_AFTER: Final = -1

    _thousandsDetector: ThousandsDetector
    _unitToConverter: UnitToConverterMap

    def __init__(
        self,
        unitToConverter: UnitToConverterMap,
        thousandsDetector: ThousandsDetector,
    ):
        self._thousandsDetector = thousandsDetector
        self._unitToConverter = unitToConverter

    def parseText(self, text: str) -> UnitParseResult | None:
        # Remove all whitespace from anywhere in the string
        textSplit = text.split()
        text = ''.join(textSplit).lower()

        # Test if it meets required format and split into groups
        regexResult = re.match(self._PATTERN_IS_NUMBER_AND_TEXT, text)

        if regexResult is None:
            return None

        # Split into number and unit by regex groups
        unitIndexes = regexResult.regs[4]
        unitString = text[unitIndexes[0]:unitIndexes[1]]

        if unitString not in self._unitToConverter:
            return None

        numberIndexes = regexResult.regs[1]
        numberString = text[numberIndexes[0]:numberIndexes[1]]
        number = self._thousandsDetector.parseNumber(numberString)

        if number is None:
            return None

        return UnitParseResult(number, unitString, UnitGroup.UNIT_AFTER)
