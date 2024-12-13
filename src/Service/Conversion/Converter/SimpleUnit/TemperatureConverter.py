from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


class TemperatureConverter(SimpleConverterInterface):
    _primaryIdCelsius = 'c'
    _primaryIdFahrenheit = 'f'
    _maxValue = 999_999

    _enabled: bool
    # TODO add more exact type hint
    _primaryUnit: dict
    _units = {
        _primaryIdCelsius: {
            'aliases': [
                '°C', 'Celsius', '°Celsius', '*Celsius',
                # Common misspellings:
                'Celcius',
            ],
            'prettyFormat': '°C',
        },
        _primaryIdFahrenheit: {
            'aliases': [
                '°F', 'Fahrenheit', '°Fahrenheit', '*Fahrenheit',
                # Common misspellings:
                'Farenheit', 'Farenheight', 'Ferenheit', 'Ferenheight', 'Ferinheit', 'Ferinheight', 'Fahrinheight',
            ],
            'prettyFormat': '°F',
        },
    }
    _unitsProcessed: dict

    def __init__(self, unitPreprocessor: UnitPreprocessor, config: Configuration):
        self._unitsProcessed = unitPreprocessor.process(self._units)
        primaryUnitId = config.get(ConfigId.Converter_Temperature_PrimaryUnit).lower()
        self._primaryUnit = self._unitsProcessed[primaryUnitId]
        self._enabled = config.get(ConfigId.Converter_Temperature_Enabled)

    def isEnabled(self) -> bool:
        return self._enabled

    def getName(self) -> str:
        return 'Temp'

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception('Cannot getUnitIds for disabled TemperatureConverter')

        return list(self._unitsProcessed.keys())

    def tryConvert(self, number: float, unitId: str) -> (bool, ConvertResult | None):
        unitFrom = self._unitsProcessed[unitId]

        if unitFrom == self._primaryUnit:
            return False, None

        if abs(number) > self._maxValue:
            return False, None

        if unitFrom['primaryId'] == self._primaryIdCelsius:
            # C to F
            convertedNumber = (number * 1.8) + 32
            convertedUnit = self._unitsProcessed[self._primaryIdFahrenheit]
        elif unitFrom['primaryId'] == self._primaryIdFahrenheit:
            # F to C
            convertedNumber = (number - 32) / 1.8
            convertedUnit = self._unitsProcessed[self._primaryIdCelsius]
        else:
            raise Exception(f'Unknown unitFrom.primaryId "{unitFrom["primaryId"]}" in TemperatureConverter')

        textFrom = f'{round(number)} {unitFrom["prettyFormat"]}'
        textTo = f'{round(convertedNumber)} {convertedUnit["prettyFormat"]}'

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())
