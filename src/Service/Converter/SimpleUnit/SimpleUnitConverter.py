import re

from src.DTO.ConvertResult import ConvertResult
from src.Service.Conversion.ThousandsDetector import ThousandsDetector
from src.Service.Converter.ConverterInterface import ConverterInterface
from src.Service.Converter.SimpleUnit.TemperatureConverter import TemperatureConverter


class SimpleUnitConverter(ConverterInterface):
    """
    Convert simple units, where a single number is followed by a single unit, e.g.: 50 km/h
    """

    _patternIsNumberAndText = re.compile('^((\\-)?([\\d,.]+))([a-z/*°]+)')

    _temperatureConverter: TemperatureConverter
    _thousandsDetector: ThousandsDetector

    def __init__(self, temperatureConverter: TemperatureConverter, thousandsDetector: ThousandsDetector):
        self._temperatureConverter = temperatureConverter
        self._thousandsDetector = thousandsDetector

    def getConverterName(self) -> str:
        return 'Simple'

    def tryConvert(self, text: str) -> (bool, ConvertResult | None):
        number, unit = self._parseText(text)

        if number is None:
            return False, None

        return False, None

    def _parseText(self, text: str) -> (float | None, str | None):
        # Remove all whitespace from anywhere in the string
        textSplit = text.split()
        text = ''.join(textSplit).lower()

        # Test if it meets basic format of number and following text
        regexResult = re.match(self._patternIsNumberAndText, text)

        if regexResult is None:
            return None, None

        # Get by regex group to split into number and unit
        numberIndexes = regexResult.regs[1]
        numberString = text[numberIndexes[0]:numberIndexes[1]]
        number = self._thousandsDetector.parseNumber(numberString)

        if number is None:
            return None, None

        unitIndexes = regexResult.regs[4]
        unitString = text[unitIndexes[0]:unitIndexes[1]]

        return number, unitString
