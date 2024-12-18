import sys

from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Converter.AbstractUnit import AbstractUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.AbstractSimpleConverter import AbstractSimpleConverter
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


class DistanceUnit(AbstractUnit):
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
        super().__init__(primaryAlias, prettyFormat)
        self.isMetric = isMetric
        self.convertToThis = convertToThis
        self.limitToShowUnit = limitToShowUnit
        self.multiplierToMeter = multiplierToMeter

class DistanceConverter(AbstractSimpleConverter):
    _maxValueMeters = 999_999 * 1000 # 1M km
    _minValueMeters = 0.0001 # 0.1 mm

    _primaryUnitMetric: bool
    _unitsDefinition: dict[str, UnitDefinition[DistanceUnit]]
    _unitsExpanded: dict[str, DistanceUnit]

    def __init__(self, config: Configuration):
        enabled = config.get(ConfigId.Converter_Distance_Enabled)
        super().__init__(enabled)

        self._primaryUnitMetric = config.get(ConfigId.Converter_Distance_PrimaryUnit_Metric)

        self._unitsDefinition = self._getUnitsDefinition()
        self._unitsExpanded = UnitPreprocessor.expandAliases(self._unitsDefinition)

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
        unitTo: DistanceUnit | None = None

        for _, unitDef in self._unitsDefinition.items():
            unitIteration = unitDef.unit
            if unitIteration.isMetric != self._primaryUnitMetric or not unitIteration.convertToThis:
                continue

            numberTo = meters / unitIteration.multiplierToMeter

            if numberTo >= unitIteration.limitToShowUnit:
                continue

            unitTo = unitIteration

            break

        numberFromRounded = round(number, 1)
        numberToRounded = round(numberTo, 1)

        textFrom = f'{numberFromRounded:g} {unitFrom.prettyFormat}'
        textTo = f'{numberToRounded:g} {unitTo.prettyFormat}'

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())

    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[DistanceUnit]]:
        return {
            # Units must be increasing order (per metric/imperial system)

            # Metric units
            'mm': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['millimeter', 'milimeter', 'millimetre', 'milimetre']),
                DistanceUnit(
                    'mm',
                    'mm',
                    True,
                    True,
                    10,
                    0.001,
                ),
            ),
            'cm': UnitDefinition(
                ['cms'] + UnitPreprocessor.pluralizeAliases(['centimeter', 'centimetre']),
                DistanceUnit(
                    'cm',
                    'cm',
                    True,
                    True,
                    100,
                    0.01,
                ),
            ),
            'dm': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['decimeter', 'decimetre']),
                DistanceUnit(
                    'dm',
                    'dm',
                    True,
                    False,
                    0,
                    0.1,
                ),
            ),
            'm': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['meter', 'metre']),
                DistanceUnit(
                    'm',
                    'm',
                    True,
                    True,
                    1000,
                    1,
                ),
            ),
            'km': UnitDefinition(
                ['kms'] + UnitPreprocessor.pluralizeAliases(['kilometer', 'killometer', 'kilometre', 'killometre']),
                DistanceUnit(
                    'km',
                    'km',
                    True,
                    True,
                    sys.maxsize,
                    1000,
                ),
            ),

            # Imperial units
            'in': UnitDefinition(
                ['ins', 'inch', 'inches', 'inchs', '"', '\'\'', '``'],
                DistanceUnit(
                    'in',
                    'in',
                    False,
                    True,
                    12,
                    0.0254,
                ),
            ),
            'ft': UnitDefinition(
                ['fts', 'feet', 'feets', 'foot', 'foots', '\'', '`'],
                DistanceUnit(
                    'ft',
                    'ft',
                    False,
                    True,
                    1000,
                    0.3048,
                ),
            ),
            'yd': UnitDefinition(
                ['yds', 'yrd', 'yrds', 'yard', 'yards'],
                DistanceUnit(
                    'yd',
                    'yd',
                    False,
                    False,
                    0,
                    0.9144,
                ),
            ),
            'mi': UnitDefinition(
                ['mile', 'miles'],
                DistanceUnit(
                    'mi',
                    'mi',
                    False,
                    True,
                    sys.maxsize,
                    1609.344,
                ),
            ),
        }
