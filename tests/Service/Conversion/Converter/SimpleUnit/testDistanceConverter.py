from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.Service.Conversion.Converter.SimpleUnit.DistanceConverter import DistanceConverter
from tests.Service.Conversion.Converter.SimpleUnit.AbstractSimpleUnitConverterTest import \
    AbstractSimpleUnitConverterTest
from tests.TestUtil.MockLibrary import MockLibrary


class TestDistanceConverter(AbstractSimpleUnitConverterTest):
    @parameterized.expand([
        # TODO rounding could be improved:
        # Eg: "0.0035 fl oz" (selected text) => "0 fl oz = ..." (shown in the statusbar)
        # More examples commented on specific test cases below
        #
        # Maybe manually specifying zeroes based on digits count would be better?

        ('To mm', 0.3, 'in', 'metric', True, '0.3 in', '7.6 mm'),
        ('To cm', 30, 'inches', 'metric', True, '30 in', '76.2 cm'),
        ('To m', 5.5, 'ft', 'metric', True, '5.5 ft', '1.7 m'),
        ('Many m', 3277.56, 'feet', 'metric', True, '3277.6 ft', '999 m'),
        ('From yd', 100, 'yd', 'metric', True, '100 yd', '91.4 m'),
        ('To km', 62, 'mi', 'metric', True, '62 mi', '99.8 km'),

        ('To in', 5, 'cms', 'imperial', True, '5 cm', '2 in'),  # Rounds 1.96 in => 2 in
        ('From dm', 5, 'dm', 'imperial', True, '5 dm', '1.6 ft'),
        ('To ft', 1.85, 'm', 'imperial', True, '1.9 m', '6.1 ft'), # Rounds 1.85 m => 1.9 m
        ('To mi', 100, 'km', 'imperial', True, '100 km', '62.1 mi'),

        ('Almost zero', 0.3, 'mm', 'imperial', True, '0.3 mm', '0 in'),
        ('Lots of small unit', 123456, 'mm', 'imperial', True, '123456 mm', '405 ft'),
        ('Little of big', 0.000001, 'mi', 'metric', True, '0 mi', '1.6 mm'),

        ('Do not convert primary unit: metric', 10, 'm', 'metric', False),
        ('Do not convert primary unit: imperial', 10, 'ft', 'imperial', False),
    ])
    def testConversion(
        self, _: str,
        number: float, unitId: str, primaryUnitSystem: str,
        expectedSuccess: bool, expectedFrom: str | None = None, expectedTo: str | None = None,
    ) -> None:
        configMock = MockLibrary.getConfig([
            (ConfigId.Converter_Distance_Enabled, True),
            (ConfigId.Converter_Distance_PrimaryUnit_Metric, True if primaryUnitSystem == 'metric' else False)
        ])
        converter = DistanceConverter(configMock)

        self._testTryConvert(converter, number, unitId, expectedSuccess, expectedFrom, expectedTo)
