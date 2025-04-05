import sys

from src.Constant.ConfigId import ConfigId
from src.DTO.Converter.MetricImperialUnit import MetricImperialUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Unit.MetricImperial.AbstractMetricImperialConverter import AbstractMetricImperialConverter
from src.Service.Conversion.Unit.UnitPreprocessor import UnitPreprocessor


class VolumeConverter(AbstractMetricImperialConverter):
    def __init__(self, config: Configuration):
        enabled = config.get(ConfigId.Converter_Volume_Enabled)
        primaryUnitMetric = config.get(ConfigId.Converter_Volume_PrimaryUnit_Metric)

        super().__init__(
            enabled,
            primaryUnitMetric,
            999_999,  # 1M L
            0.0001,  # 0.1 mL / 100 mm3
        )

    def getName(self) -> str:
        return 'Vol'

    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[MetricImperialUnit]]:
        return {
            # Units must be increasing order (per metric/imperial system)

            # Metric units
            'mm3': UnitDefinition(
                ['millimeter3', 'milimeter3', 'millimetre3', 'milimetre3', 'cubicmm']
                + UnitPreprocessor.pluralizeAliases([
                    'cubicmillimeter', 'cubicmilimeter', 'cubicmillimetre', 'cubicmilimetre',
                ]),
                MetricImperialUnit(
                    'mm3',
                    'mm3',
                    True,
                    True,
                    1000,
                    0.000001,
                ),
            ),
            'ml / cm3': UnitDefinition(
                ['cm3', 'centimeter3', 'centimetre3', 'cubiccm', 'cubiccentimeter', 'cubiccentimetre']
                + UnitPreprocessor.pluralizeAliases([
                    'milliliter', 'mililiter', 'millilitre', 'mililitre',
                ]),
                MetricImperialUnit(
                    'ml',
                    'ml',
                    True,
                    True,
                    1000,
                    0.001,
                ),
            ),
            'cl (10 ml)': UnitDefinition(
                UnitPreprocessor.pluralizeAliases([
                    'centiliter', 'centilitre', 'centliter', 'centlitre',
                ]),
                MetricImperialUnit(
                    'cl',
                    'cl',
                    True,
                    False,
                    -1,
                    0.01,
                ),
            ),
            'dl (100 ml)': UnitDefinition(
                UnitPreprocessor.pluralizeAliases([
                    'deciliter', 'decilitre',
                ]),
                MetricImperialUnit(
                    'dl',
                    'dl',
                    True,
                    False,
                    -1,
                    0.1,
                ),
            ),
            'l': UnitDefinition(
                UnitPreprocessor.pluralizeAliases([
                    'liter', 'litre',
                ]),
                MetricImperialUnit(
                    'l',
                    'l',
                    True,
                    True,
                    sys.maxsize,
                    1,
                ),
            ),
            'm3': UnitDefinition(
                ['meter3', 'metre3',]
                + UnitPreprocessor.pluralizeAliases([
                    'cubicmeter', 'cubicmetre',
                ]),
                MetricImperialUnit(
                    'm3',
                    'm3',
                    True,
                    False,
                    -1,
                    1000,
                ),
            ),

            # Imperial (US) units
            # TODO improve by adding UK imperial units
            #  They are slightly different than US sizes, but have same names.
            #  Should have a 3-way selector for primary unit: metric, Imperial (US), Imperial (UK)
            'fl oz': UnitDefinition(
                ['fl.oz', 'fl.oz.'],
                MetricImperialUnit(
                    'fl oz',
                    'fl oz',
                    False,
                    True,
                    128,  # 128 fl oz = 1 gal
                    1 / 29.57353,
                )
            ),
            'gal': UnitDefinition(
                ['gals'] +
                UnitPreprocessor.pluralizeAliases([
                    'gallon', 'galon',
                ]),
                MetricImperialUnit(
                    'gal',
                    'gal',
                    False,
                    True,
                    sys.maxsize,
                    0.2641720524,
                ),
            ),
            'tablespoon': UnitDefinition(
                ['tablespoon', 'tablespoons', 'tbsp.', 'tb', 'tb.'],
                MetricImperialUnit(
                    'tbsp',
                    'tbsp',
                    False,
                    False,
                    -1,
                    0.0148,
                ),
            ),
            'teaspoon': UnitDefinition(
                ['teaspoon', 'teaspoons', 'tsp.', 'ts', 'ts.', 'tspn', 'tspn.'],
                MetricImperialUnit(
                    'tsp',
                    'tsp',
                    False,
                    False,
                    -1,
                    0.0049289,
                ),
            ),
        }
