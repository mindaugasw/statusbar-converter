from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestTemperatureConverter(AbstractConversionManagerTest):
    @parameterized.expand([
        ('Simple C->F', 'f', '100 c', True, '100 °C', '212 °F'),
        ('Simple F->C', 'C', '212 f', True, '212 °F', '100 °C'),
        ('Different alias', 'f', '100 *celsius', True, '100 °C', '212 °F'),
        ('Negative', 'f', '-100 c', True, '-100 °C', '-148 °F'),
        ('Max value', 'f', '999999 c', True, '999999 °C', '1800030 °F'),
        ('Over max value', 'f', '1000000 c', False),
        ('Negative max value', 'f', '-999999 c', True, '-999999 °C', '-1799966 °F'),
        ('Over negative max value', 'f', '-1000000 c', False),
        ('Decimal values', 'f', '5.7 c', True, '6 °C', '42 °F'),
        ('Do not convert primary unit: C', 'c', '100 c', False),
        ('Do not convert primary unit: F', 'f', '100 f', False),
        ('Whitespace', 'f', '100 \n ° \t c', True, '100 °C', '212 °F'),
    ])
    def testTemperatureConverter(
        self, _: str,
        primaryUnitId: str,
        text: str, expectSuccess: bool, expectFrom: str | None = None, expectTo: str | None = None,
    ) -> None:
        configOverrides = [
            (ConfigId.Converter_Temperature_PrimaryUnit, primaryUnitId),
        ]

        self.runConverterTest(text, expectSuccess, expectFrom, expectTo, configOverrides)
