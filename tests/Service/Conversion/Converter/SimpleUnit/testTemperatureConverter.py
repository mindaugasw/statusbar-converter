from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.Service.Conversion.Converter.SimpleUnit.TemperatureConverter import TemperatureConverter
from tests.Service.Conversion.Converter.SimpleUnit.AbstractSimpleUnitConverterTest import \
    AbstractSimpleUnitConverterTest
from tests.TestUtil.MockLibrary import MockLibrary


class TestTemperatureConverter(AbstractSimpleUnitConverterTest):
    @parameterized.expand([
        ('Simple C->F', 100, 'c', 'f', True, '100 °C', '212 °F'),
        ('Simple F->C', 212, 'f', 'C', True, '212 °F', '100 °C'),
        ('Different alias', 100, '*celsius', 'f', True, '100 °C', '212 °F'),
        ('Negative', -100, 'c', 'f', True, '-100 °C', '-148 °F'),
        ('Max value', 999_999, 'c', 'f', True, '999999 °C', '1800030 °F'),
        ('Over max value', 1_000_000, 'c', 'f', False),
        ('Negative max value', -999_999, 'c', 'f', True, '-999999 °C', '-1799966 °F'),
        ('Over negative max value', -1_000_000, 'c', 'f', False),
        ('Decimal values', 5.7, 'c', 'f', True, '6 °C', '42 °F'),
        ('Do not convert primary unit: C', 100, 'c', 'c', False),
        ('Do not convert primary unit: F', 100, 'f', 'f', False),
    ])
    def testTryConvert(
        self, _: str,
        number: float, unitId: str, primaryUnitId: str,
        expectedSuccess: bool, expectedFrom: str | None = None, expectedTo: str | None = None,
    ) -> None:
        configMock = MockLibrary.getConfig([
            (ConfigId.Converter_Temperature_Enabled, True),
            (ConfigId.Converter_Temperature_PrimaryUnit, primaryUnitId),
        ])
        converter = TemperatureConverter(configMock)

        self._testTryConvert(converter, number, unitId, expectedSuccess, expectedFrom, expectedTo)
