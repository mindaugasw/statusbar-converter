from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Converter.AbstractUnit import AbstractUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.AbstractSimpleConverter import AbstractSimpleConverter
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor

class TemperatureUnit(AbstractUnit):
    pass

class TemperatureConverter(AbstractSimpleConverter):
    _primaryAliasCelsius = 'c'
    _primaryAliasFahrenheit = 'f'
    _maxValue = 999_999

    _unitsExpanded: dict[str, TemperatureUnit]
    _primaryUnit: TemperatureUnit

    def __init__(self, config: Configuration):
        enabled = config.get(ConfigId.Converter_Temperature_Enabled)
        super().__init__(enabled)

        self._unitsExpanded = UnitPreprocessor.expandAliases(self._getUnitsDefinition())

        primaryUnitId = config.get(ConfigId.Converter_Temperature_PrimaryUnit).lower()
        self._primaryUnit = self._unitsExpanded[primaryUnitId]

    def getName(self) -> str:
        return 'Temp'

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception('Cannot getUnitIds for disabled TemperatureConverter')

        return list(self._unitsExpanded.keys())

    def tryConvert(self, number: float, unitId: str) -> (bool, ConvertResult | None):
        unitFrom = self._unitsExpanded[unitId]

        if unitFrom == self._primaryUnit:
            return False, None

        if abs(number) > self._maxValue:
            return False, None

        if unitFrom.primaryAlias == self._primaryAliasCelsius:
            # C to F
            numberTo = (number * 1.8) + 32
            unitTo = self._unitsExpanded[self._primaryAliasFahrenheit]
        elif unitFrom.primaryAlias == self._primaryAliasFahrenheit:
            # F to C
            numberTo = (number - 32) / 1.8
            unitTo = self._unitsExpanded[self._primaryAliasCelsius]
        else:
            raise Exception(f'Unknown unitFrom.primaryAlias "{unitFrom.primaryAlias}" in TemperatureConverter')

        textFrom = f'{round(number)} {unitFrom.prettyFormat}'
        textTo = f'{round(numberTo)} {unitTo.prettyFormat}'

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())

    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[TemperatureUnit]]:
        return {
            'c': UnitDefinition(
                [
                    '°C', 'Celsius', '°Celsius', '*Celsius',
                    # Common misspellings:
                    'Celcius',
                ],
                TemperatureUnit(
                    self._primaryAliasCelsius,
                    '°C',
                ),
            ),
            'f': UnitDefinition(
                [
                    '°F', 'Fahrenheit', '°Fahrenheit', '*Fahrenheit',
                    # Common misspellings:
                    'Farenheit', 'Farenheight', 'Ferenheit', 'Ferenheight', 'Ferinheit', 'Ferinheight', 'Fahrinheight',
                ],
                TemperatureUnit(
                    self._primaryAliasFahrenheit,
                    '°F',
                ),
            ),
        }
