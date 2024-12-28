import sys

from src.Constant.ConfigId import ConfigId
from src.DTO.Converter.MetricImperialUnit import MetricImperialUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.AbstractMetricImperialConverter import AbstractMetricImperialConverter
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


class WeightConverter(AbstractMetricImperialConverter):
    def __init__(self, config: Configuration):
        enabled = config.get(ConfigId.Converter_Weight_Enabled)
        primaryUnitMetric = config.get(ConfigId.Converter_Weight_PrimaryUnit_Metric)

        super().__init__(
            enabled,
            primaryUnitMetric,
            999_999,  # 1M kg
            0.0000001,  # 0.1 mg
        )

    def getName(self) -> str:
        return 'Weight'

    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[MetricImperialUnit]]:
        units = {
            # Units must be increasing order (per metric/imperial system)

            # Metric
            'mg': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['milligram', 'miligram']),
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                    MetricImperialUnit(
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
                #     MetricImperialUnit(
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
                    MetricImperialUnit(
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
                #     MetricImperialUnit(
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
