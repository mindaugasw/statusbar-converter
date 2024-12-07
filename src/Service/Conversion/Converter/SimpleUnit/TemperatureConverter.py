from src.DTO.ConvertResult import ConvertResult
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


class TemperatureConverter(SimpleConverterInterface):
    _units = {
        'C': {
            'aliases': ['°C', 'Celsius', '°Celsius', '*Celsius'],
        },
        'F': {
            'aliases': ['°F', 'Fahrenheit', '°Fahrenheit', '*Fahrenheit'],
        },
        # TODO additional properties:
        # pretty print format
        # consider min-max range? May help with correctly guessing if it's thousands or decimal separator
    }
    _unitsProcessed: dict

    def __init__(self, unitPreprocessor: UnitPreprocessor, config: Configuration):
        self._unitsProcessed = unitPreprocessor.process(self._units)

        # TODO check config if converter is enabled

    def getName(self) -> str:
        return 'Temp'

    def getUnitIds(self) -> list[str]:
        return list(self._unitsProcessed.keys())

    def tryConvert(self, number: float, unit: str) -> (bool, ConvertResult | None):
        # return False, None
        return True, ConvertResult('5 C = 10 F', '5 C', '10 F', self.getName())