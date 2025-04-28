from typing import Tuple

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Converter.CurrencyUnit import CurrencyUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Service.Conversion.Unit.UnitPreprocessor import UnitPreprocessor
from src.Service.EventService import EventService
from src.Service.Logger import Logger


class CurrencyConverter(UnitConverterInterface):
    _events: EventService
    _config: Configuration
    _logger: Logger

    _enabled: bool
    _initialized: bool
    _primaryCurrency: str
    _unitsDefinition: dict[str, UnitDefinition[CurrencyUnit]]
    _unitsExpanded: dict[str, CurrencyUnit]

    def __init__(
        self,
        events: EventService,
        config: Configuration,
        logger: Logger,
    ):
        self._events = events
        self._config = config
        self._logger = logger

        self._enabled = config.get(ConfigId.Converter_Currency_Enabled)
        self._initialized = False
        self._primaryCurrency = config.get(ConfigId.Converter_Currency_PrimaryCurrency)

    def isEnabled(self) -> bool:
        return self._enabled

    def isDelayedInitialization(self) -> bool:
        return True

    def getName(self) -> str:
        return 'Currency'

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception(f'Cannot getUnitIds for disabled {self.getName()} converter')

        if not self._initialized:
            raise Exception(f'Cannot getUnitIds for not initialized {self.getName()} converter')

        return list(self._unitsExpanded.keys())

    def tryConvert(self, number: float, unitId: str) -> Tuple[bool, ConvertResult | None]:
        fromCurrency = self._unitsExpanded[unitId]
        targetCurrency = self._unitsExpanded[self._primaryCurrency]

        if fromCurrency is targetCurrency:
            return False, None

        targetCurrencyAmount = (number / fromCurrency.rate) * targetCurrency.rate

        textFrom = f'{number:g} {fromCurrency.prettyFormat}'
        textTo = f'{targetCurrencyAmount:g} {targetCurrency.prettyFormat}'

        # TODO add special case if converter from number=1, then show more decimal numbers

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())

    def refreshUnits(self, data: dict) -> None:
        self._unitsDefinition = self._getUnitsDefinition(data)
        self._unitsExpanded = UnitPreprocessor.expandAliases(self._unitsDefinition)

        if not self._primaryCurrency in self._unitsDefinition:
            defaultPrimaryCurrency = ConfigId.Converter_Currency_PrimaryCurrency.defaultValue

            self._logger.log(
                f'{Logs.catConverter}Currency] WARNING: selected primary currency ({self._primaryCurrency}) is no '
                f'longer present in currencies list after refresh. Resetting to default '
                f'({defaultPrimaryCurrency})',
            )

            self._config.set(ConfigId.Converter_Currency_PrimaryCurrency, defaultPrimaryCurrency)

        self._initialized = True
        self._events.dispatchDelayedConverterInitialized(self)

    def _getUnitsDefinition(self, data: dict) -> dict[str, UnitDefinition[CurrencyUnit]]:
        unitsDefinition = {}

        for key, currency in data.items():
            unitsDefinition[key] = UnitDefinition(
                currency['aliases'] + UnitPreprocessor.pluralizeAliases(currency['aliasesToPluralize']),
                CurrencyUnit(
                    currency['primaryAlias'],
                    currency['prettyFormat'],
                    currency['rate'],
                ),
            )

        return unitsDefinition
