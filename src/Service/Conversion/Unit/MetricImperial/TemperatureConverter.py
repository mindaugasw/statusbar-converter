from typing import Tuple, Final

from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Converter.AbstractUnit import AbstractUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Service.Conversion.Unit.UnitPreprocessor import UnitPreprocessor


class TemperatureUnit(AbstractUnit):
    pass

class TemperatureConverter(UnitConverterInterface):
    _PRIMARY_ALIAS_CELSIUS: Final[str] = 'c'
    _PRIMARY_ALIAS_FAHRENHEIT: Final[str] = 'f'
    _MAX_VALUE: Final[int] = 999_999

    _enabled: bool
    _unitsExpanded: dict[str, TemperatureUnit]
    _primaryUnit: TemperatureUnit

    def __init__(self, config: Configuration):
        self._enabled = config.get(ConfigId.Converter_Temperature_Enabled)
        self._unitsExpanded = UnitPreprocessor.expandAliases(self._getUnitsDefinition())

        primaryUnitId = self._PRIMARY_ALIAS_CELSIUS\
            if config.get(ConfigId.Converter_Temperature_PrimaryUnit_Celsius)\
            else self._PRIMARY_ALIAS_FAHRENHEIT
        self._primaryUnit = self._unitsExpanded[primaryUnitId]

    def isEnabled(self) -> bool:
        return self._enabled

    def isDelayedInitialization(self) -> bool:
        return False

    def getName(self) -> str:
        return 'Temp'

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception('Cannot getUnitIds for disabled TemperatureConverter')

        return list(self._unitsExpanded.keys())

    def tryConvert(self, number: float, unitId: str) -> Tuple[bool, ConvertResult | None]:
        unitFrom = self._unitsExpanded[unitId]

        if unitFrom == self._primaryUnit:
            return False, None

        if abs(number) > self._MAX_VALUE:
            return False, None

        if unitFrom.primaryAlias == self._PRIMARY_ALIAS_CELSIUS:
            # C to F
            numberTo = (number * 1.8) + 32
            unitTo = self._unitsExpanded[self._PRIMARY_ALIAS_FAHRENHEIT]
        elif unitFrom.primaryAlias == self._PRIMARY_ALIAS_FAHRENHEIT:
            # F to C
            numberTo = (number - 32) / 1.8
            unitTo = self._unitsExpanded[self._PRIMARY_ALIAS_CELSIUS]
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
                    self._PRIMARY_ALIAS_CELSIUS,
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
                    self._PRIMARY_ALIAS_FAHRENHEIT,
                    '°F',
                ),
            ),
        }
