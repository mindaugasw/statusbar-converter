import sys

from src.Constant.ConfigId import ConfigId
from src.DTO.Converter.MetricImperialUnit import MetricImperialUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.SimpleUnit.AbstractMetricImperialConverter import AbstractMetricImperialConverter
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor


class DistanceConverter(AbstractMetricImperialConverter):
    def __init__(self, config: Configuration):
        enabled = config.get(ConfigId.Converter_Distance_Enabled)
        primaryUnitMetric = config.get(ConfigId.Converter_Distance_PrimaryUnit_Metric)

        super().__init__(
            enabled,
            primaryUnitMetric,
            999_999 * 1000,  # 1M km
            0.0001,  # 0.1 mm
        )

    def getName(self) -> str:
        return 'Dist'

    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[MetricImperialUnit]]:
        return {
            # Units must be increasing order (per metric/imperial system)

            # Metric units
            'mm': UnitDefinition(
                UnitPreprocessor.pluralizeAliases(['millimeter', 'milimeter', 'millimetre', 'milimetre']),
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
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
                MetricImperialUnit(
                    'mi',
                    'mi',
                    False,
                    True,
                    sys.maxsize,
                    1609.344,
                ),
            ),
        }
