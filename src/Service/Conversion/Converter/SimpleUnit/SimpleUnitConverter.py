import re

from src.DTO.ConvertResult import ConvertResult
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.AbstractSimpleConverter import AbstractSimpleConverter
from src.Service.Conversion.ThousandsDetector import ThousandsDetector


class SimpleUnitConverter(ConverterInterface):
    """
    Convert simple units, where a single number is followed by a single unit, e.g.: 50 km/h
    """

    _thousandsDetector: ThousandsDetector

    _patternIsNumberAndText = re.compile(r'^((\-)?([\d,.]*\d[\d,.]*))([a-z/*°\'"`.]+)')
    _unitToConverter: dict[str, AbstractSimpleConverter]
    _enabled: bool

    def __init__(self, internalConverters: list[AbstractSimpleConverter], thousandsDetector: ThousandsDetector):
        self._thousandsDetector = thousandsDetector
        self._unitToConverter = {}

        for internalConverter in internalConverters:
            if not internalConverter.isEnabled():
                continue

            unitsIds = internalConverter.getUnitIds()

            for unitId in unitsIds:
                if unitId in self._unitToConverter:
                    raise Exception(f'SimpleUnitConverter unit alias collision: {unitId} alias already exists')

                self._unitToConverter[unitId] = internalConverter

        self._enabled = len(self._unitToConverter) > 0

    def isEnabled(self) -> bool:
        return self._enabled

    def getName(self) -> str:
        return 'Simple'

    def tryConvert(self, text: str) -> (bool, ConvertResult | None):
        number, unit = self._parseText(text)

        if number is None or unit is None:
            return False, None

        success, result = self._unitToConverter[unit].tryConvert(number, unit)

        if result is None:
            return False, None

        result.converterName = f'{self.getName()}.{result.converterName}'

        return True, result

    def _parseText(self, text: str) -> (float | None, str | None):
        # Remove all whitespace from anywhere in the string
        textSplit = text.split()
        text = ''.join(textSplit).lower()

        # Test if it meets basic format of number followed by text
        regexResult = re.match(self._patternIsNumberAndText, text)

        if regexResult is None:
            return None, None

        # Split into number and unit by regex groups
        unitIndexes = regexResult.regs[4]
        unitString = text[unitIndexes[0]:unitIndexes[1]]

        if unitString not in self._unitToConverter:
            return None, None

        numberIndexes = regexResult.regs[1]
        numberString = text[numberIndexes[0]:numberIndexes[1]]
        number = self._thousandsDetector.parseNumber(numberString)

        if number is None:
            return None, None

        return number, unitString
