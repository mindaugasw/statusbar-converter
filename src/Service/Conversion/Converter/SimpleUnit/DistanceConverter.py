import sys

from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


class DistanceUnitExpanded:
    primaryAlias: str
    prettyFormat: str
    isMetric: bool
    convertToThis: bool
    limitToShowUnit: float
    multiplierToMeter: float

    def __init__(
        self,
        primaryAlias: str,
        prettyFormat: str,
        isMetric: bool,
        convertToThis: bool,
        limitToShowUnit: float,
        multiplierToMeter: float,
    ):
        self.primaryAlias = primaryAlias
        self.prettyFormat = prettyFormat
        self.isMetric = isMetric
        self.convertToThis = convertToThis
        self.limitToShowUnit = limitToShowUnit
        self.multiplierToMeter = multiplierToMeter

class DistanceUnitInitial(DistanceUnitExpanded):
    aliases: list[str]

    def __init__(
        self,
        primaryAlias: str,
        aliases: list[str],
        prettyFormat: str,
        isMetric: bool,
        convertToThis: bool,
        limitToShowUnit: float,
        multiplierToMeter: float,
    ):
        super().__init__(primaryAlias, prettyFormat, isMetric, convertToThis, limitToShowUnit, multiplierToMeter)
        self.aliases = aliases

class DistanceConverter(SimpleConverterInterface):
    _maxValueMeters = 999_999 * 1000 # 1M km
    _minValueMeters = 0.0001 # 0.1 mm

    _enabled: bool
    _primaryUnitMetric: bool
    _unitsInitial: dict[str, DistanceUnitInitial]
    _unitsExpanded: dict[str, DistanceUnitExpanded]

    def __init__(self, config: Configuration):
        self._enabled = config.get(ConfigId.Converter_Distance_Enabled)
        self._primaryUnitMetric = config.get(ConfigId.Converter_Distance_PrimaryUnit_Metric)

        self._unitsInitial = self._getUnitsInitial()
        self._unitsExpanded = self._expandUnitAliases(self._unitsInitial)

    def isEnabled(self) -> bool:
        return self._enabled

    def getName(self) -> str:
        return 'Dist'

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception('Cannot getUnitIds for disabled DistanceConverter')

        return list(self._unitsExpanded.keys())

    def tryConvert(self, number: float, unitId: str) -> (bool, ConvertResult | None):
        unitFrom = self._unitsExpanded[unitId]

        if unitFrom.isMetric == self._primaryUnitMetric:
            return False, None

        meters = number * unitFrom.multiplierToMeter

        if meters > self._maxValueMeters or meters < self._minValueMeters:
            return False, None

        numberTo: float = -1
        unitTo: DistanceUnitInitial | None = None

        for _, unitInitial in self._unitsInitial.items():
            if unitInitial.isMetric != self._primaryUnitMetric or not unitInitial.convertToThis:
                continue

            numberTo = meters / unitInitial.multiplierToMeter

            if numberTo >= unitInitial.limitToShowUnit:
                continue

            unitTo = unitInitial

            break

        numberFromRounded = round(number, 1)
        numberToRounded = round(numberTo, 1)

        textFrom = f'{numberFromRounded:g} {unitFrom.prettyFormat}'
        textTo = f'{numberToRounded:g} {unitTo.prettyFormat}'

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())

    def _getUnitsInitial(self) -> dict[str, DistanceUnitInitial]:
        return {
            # Units must be increasing order (per metric/imperial system)

            # Metric units
            'mm': DistanceUnitInitial(
                'mm',
                self._pluralizeAliases(['millimeter', 'milimeter', 'millimetre', 'milimetre']),
                'mm',
                True,
                True,
                10,
                0.001,
            ),
            'cm': DistanceUnitInitial(
                'cm',
                ['cms'] + self._pluralizeAliases(['centimeter', 'centimetre']),
                'cm',
                True,
                True,
                100,
                0.01,
            ),
            'dm': DistanceUnitInitial(
                'dm',
                self._pluralizeAliases(['decimeter', 'decimetre']),
                'dm',
                True,
                False,
                0,
                0.1,
            ),
            'm': DistanceUnitInitial(
                'm',
                self._pluralizeAliases(['meter', 'metre']),
                'm',
                True,
                True,
                1000,
                1,
            ),
            'km': DistanceUnitInitial(
                'km',
                ['kms'] + self._pluralizeAliases(['kilometer', 'killometer', 'kilometre', 'killometre']),
                'km',
                True,
                True,
                sys.maxsize,
                1000,
            ),

            # Imperial units
            'in': DistanceUnitInitial(
                'in',
                ['ins', 'inch', 'inches', 'inchs', '"', '\'\'', '``'],
                '\'\'',
                False,
                True,
                12,
                0.0254,
            ),
            'ft': DistanceUnitInitial(
                'ft',
                ['fts', 'feet', 'feets', 'foot', 'foots', '\'', '`'],
                '\'',
                False,
                True,
                1000,
                0.3048,
            ),
            'yd': DistanceUnitInitial(
                'yd',
                ['yds', 'yrd', 'yrds', 'yard', 'yards'],
                'yd',
                False,
                False,
                0,
                0.9144,
            ),
            'mi': DistanceUnitInitial(
                'mi',
                ['mile', 'miles'],
                'mi',
                False,
                True,
                sys.maxsize,
                1609.344,
            ),
        }

    def _pluralizeAliases(self, aliases: list[str]) -> list[str]:
        newList: list[str] = []

        for alias in aliases:
            newList.append(alias)
            newList.append(alias + 's')

        return newList

    # TODO maybe extract to common UnitPreprocessor?
    def _expandUnitAliases(self, units: dict[str, DistanceUnitInitial]) -> dict[str, DistanceUnitExpanded]:
        unitsExpanded: dict[str, DistanceUnitExpanded] = {}

        for _, unit in units.items():
            primaryAlias = UnitPreprocessor._cleanString(unit.primaryAlias)

            unitExpanded = DistanceUnitExpanded(
                primaryAlias,
                unit.prettyFormat,
                unit.isMetric,
                unit.convertToThis,
                unit.limitToShowUnit,
                unit.multiplierToMeter,
            )
            unitsExpanded.update({primaryAlias: unitExpanded})

            for alias in unit.aliases:
                aliasCleaned = UnitPreprocessor._cleanString(alias)

                if aliasCleaned in unitsExpanded:
                    raise Exception(f'DistanceConverter unit alias collision: {aliasCleaned} alias already exists')

                unitsExpanded.update({aliasCleaned: unitExpanded})

        return unitsExpanded
