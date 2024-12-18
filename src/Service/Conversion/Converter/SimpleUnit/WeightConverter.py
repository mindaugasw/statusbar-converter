import sys

from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.AbstractSimpleConverter import AbstractSimpleConverter
from src.Service.Conversion.Converter.SimpleUnit.DistanceConverter import DistanceUnit
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


# TODO maybe convert DistanceUnit to MetricImperialUnit?
class WeightUnit(DistanceUnit):
    pass

class WeightConverter(AbstractSimpleConverter):
    _maxValueKilograms = 999_999  # 1M kg
    _minValueKilograms = 0.0000001  # 0.1 mg

    _enabled: bool
    _primaryUnitMetric: bool
    _unitsDefinition: dict[str, UnitDefinition[WeightUnit]]
    _unitsExpanded: dict[str, WeightUnit]

    def __init__(self, config: Configuration):
        enabled = config.get(ConfigId.Converter_Weight_Enabled)
        super().__init__(enabled)

        self._primaryUnitMetric = config.get(ConfigId.Converter_Weight_PrimaryUnit_Metric)
        self._unitsDefinition = self._getUnitsDefinition()
        self._unitsExpanded = UnitPreprocessor.expandAliases(self._unitsDefinition)

    def getName(self) -> str:
        return 'Weight'

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception('Cannot getUnitIds for disabled WeightConverter')

        return list(self._unitsExpanded.keys())

    def tryConvert(self, number: float, unitId: str) -> (bool, ConvertResult | None):
        unitFrom = self._unitsExpanded[unitId]

        if unitFrom.isMetric == self._primaryUnitMetric:
            return False, None

        baseUnitNumber = number * unitFrom.multiplierToMeter

        if baseUnitNumber > self._maxValueKilograms or baseUnitNumber < self._minValueKilograms:
            return False, None

        numberTo: float = -1
        unitTo: WeightUnit | None = None

        for _, unitDef in self._unitsDefinition.items():
            unitIteration = unitDef.unit

            if unitIteration.isMetric != self._primaryUnitMetric or not unitIteration.convertToThis:
                continue

            numberTo = baseUnitNumber / unitIteration.multiplierToMeter

            if numberTo >= unitIteration.limitToShowUnit:
                continue

            unitTo = unitIteration

            break

        numberFromRounded = round(number, 1)
        numberToRounded = round(numberTo, 1)

        textFrom = f'{numberFromRounded:g} {unitFrom.prettyFormat}'
        textTo = f'{numberToRounded:g} {unitTo.prettyFormat}'

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())

    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[WeightUnit]]:
        units = {
            # Units must be increasing order (per metric/imperial system)

            # Metric
            'mg': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['milligram', 'miligram']),
                WeightUnit(
                    'mg',
                    'mg',
                    True,
                    True,
                    1000,
                    0.000001,
                ),
            ),
            # centigram (cg) and decigram (dg) are skipped because they're used very rarely.
            # Copied text is more unlikely to be actual measurement to convert
            'g': UnitDefinition(
                ['gr', 'grm'] + UnitPreprocessor.pluralizeAliases(['gram', 'grame', 'gramme']),
                WeightUnit(
                    'g',
                    'g',
                    True,
                    True,
                    1000,
                    0.001
                ),
            ),
            'kg': UnitDefinition(
                ['kgs'] + UnitPreprocessor.pluralizeAliases(['kilogram', 'killogram', 'kilogramme', 'killogramme']),
                WeightUnit(
                    'kg',
                    'kg',
                    True,
                    True,
                    sys.maxsize,
                    1,
                ),
            ),

            # Imperial
            'ounce': UnitDefinition(
                ['oz.'] + UnitPreprocessor.pluralizeAliases(['ounce']),
                WeightUnit(
                    'oz',
                    'oz',
                    False,
                    True,
                    16,
                    0.02834952,
                ),
            ),
            'pound': UnitDefinition(
                ['lbs', 'lb.', 'lbs.'] + UnitPreprocessor.pluralizeAliases(['pound']),
                WeightUnit(
                    'lb',
                    'lb',
                    False,
                    True,
                    sys.maxsize,
                    0.45359237,
                ),
            ),
            'stone': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['stone']),
                WeightUnit(
                    'st',
                    'st',
                    False,
                    False,
                    -1,
                    6.35029318,
                ),
            ),
        }

        # To avoid confusion (12 t = 12.2 t), metric/imperial tons are converted kg/lb.
        # ton-to-ton conversion can be enabled by uncommenting the second unit.
        # First unit is unitFrom, used for aliases and multiplier.
        # Second unit is unitTo, used for prettyFormat and multiplier.
        if self._primaryUnitMetric:
            units.update({
                'imperial_ton': UnitDefinition(
                    UnitPreprocessor.pluralizeAliases(['ton', 'tone', 'tonne']),
                    WeightUnit(
                        't',
                        't',
                        False,
                        False,
                        -1,
                        1016.0469088,
                    ),
                ),
                # Uncomment to enable converting ton-to-ton:
                # 'metric_tonne': UnitDefinition(
                #     [],
                #     WeightUnit(
                #         'metric tonne',
                #         't',
                #         True,
                #         True,
                #         sys.maxsize,
                #         1000,
                #     )
                # ),
            })
        else:
            units.update({
                'metric_tonne': UnitDefinition(
                    UnitPreprocessor.pluralizeAliases(['ton', 'tone', 'tonne']),
                    WeightUnit(
                        't',
                        't',
                        True,
                        False,
                        -1,
                        1000,
                    ),
                ),
                # Uncomment to enable converting ton-to-ton:
                # 'imperial_ton': UnitDefinition(
                #     [],
                #     WeightUnit(
                #         'imperial ton',
                #         't',
                #         False,
                #         True,
                #         sys.maxsize,
                #         1016.0469088,
                #     ),
                # ),
            })

        return units
