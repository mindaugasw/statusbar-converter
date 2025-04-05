from unittest import TestCase

from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.Constant.UnitGroup import UnitGroup
from src.Service.Conversion.Converter.SimpleUnit.DistanceConverter import DistanceConverter
from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.TemperatureConverter import TemperatureConverter
from src.Service.Conversion.Converter.SimpleUnit.VolumeConverter import VolumeConverter
from src.Service.Conversion.Converter.SimpleUnit.WeightConverter import WeightConverter
from src.Service.Conversion.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.UnitParser import UnitParser
from src.Service.Conversion.UnitToConverterMap import UnitToConverterMap
from tests.TestUtil.MockLibrary import MockLibrary


class TestUnitParser(TestCase):
    @parameterized.expand([
        ('Simple', '5ft', 5, 'ft'),
        ('With whitespace, uppercase', ' 5 FT ', 5, 'ft'),
        ('Fractional', '5.5kg', 5.5, 'kg'),
        ('Special symbols ft', '18\'', 18, '\''),
        ('Special symbols in', '18"', 18, '"'),
        ('Unit with number', '3m3', 3, 'm3'),

        # Compound units like 5'11" generally are not supported. But current parsers
        # already half-parse them, treating as 5ft (cutting off inches).
        # So we test to ensure this compatibility remains
        ('Compound ft in', '18′5″', 18, '′'),

        # Should not be matched
        ('Not existing unit', '5ab'),
        ('Invalid 1', '5'),
        ('Invalid 2', '5.5'),
        ('Invalid 3', 'a'),
        ('Invalid 4', '-'),
        ('Invalid 5', ' '),
        ('Invalid 6', '3 3'),
    ])
    def testParseText(
        self, _: str,
        text: str,
        expectNumber: float | None = None, expectUnit: str | None = None,
    ) -> None:
        parser = self._getParser()

        result = parser.parseText(text)

        if expectNumber is None:
            self.assertEqual(None, result)
        else:
            self.assertEqual(expectNumber, result.number)
            self.assertEqual(expectUnit, result.unit)
            self.assertEqual(UnitGroup.UNIT_AFTER, result.unitGroup)

    def _getParser(self) -> UnitParser:
        config = [
            (ConfigId.Converter_Distance_Enabled, True),
            (ConfigId.Converter_Distance_PrimaryUnit_Metric, True),
            (ConfigId.Converter_Temperature_Enabled, True),
            (ConfigId.Converter_Temperature_PrimaryUnit_Celsius, True),
            (ConfigId.Converter_Volume_Enabled, True),
            (ConfigId.Converter_Volume_PrimaryUnit_Metric, True),
            (ConfigId.Converter_Weight_Enabled, True),
            (ConfigId.Converter_Weight_PrimaryUnit_Metric, True),
        ]

        configMock = MockLibrary.getConfig(config)

        simpleConverters: list[SimpleConverterInterface] = [
            DistanceConverter(configMock),
            WeightConverter(configMock),
            TemperatureConverter(configMock),
            VolumeConverter(configMock),
        ]

        unitToConverterMap = UnitToConverterMap(simpleConverters)

        return UnitParser(unitToConverterMap, ThousandsDetector())
