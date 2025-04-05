from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestDistanceConverter(AbstractConversionManagerTest):
    @parameterized.expand([
        # TODO rounding could be improved:
        # Eg: "0.0035 fl oz" (selected text) => "0 fl oz = ..." (shown in the statusbar)
        # More examples commented on specific test cases below
        #
        # Maybe manually specifying zeroes based on digits count would be better?

        ('To mm', 'metric', '0.3 in', True, '0.3 in', '7.6 mm'),
        ('To cm', 'metric', '30 inches', True, '30 in', '76.2 cm'),
        ('To m', 'metric', '5.5 ft', True, '5.5 ft', '1.7 m'),
        ('Many m', 'metric', '3277.56 feet', True, '3277.6 ft', '999 m'),
        ('From yd', 'metric', '100 yd', True, '100 yd', '91.4 m'),
        ('To km', 'metric', '62 mi', True, '62 mi', '99.8 km'),

        ('To in', 'imperial', '5 cms', True, '5 cm', '2 in'),  # Rounds 1.96 in => 2 in
        ('From dm', 'imperial', '5 dm', True, '5 dm', '1.6 ft'),
        ('To ft', 'imperial', '1.85 m', True, '1.9 m', '6.1 ft'),  # Rounds 1.85 m => 1.9 m
        ('To mi', 'imperial', '100 km', True, '100 km', '62.1 mi'),

        ('Almost zero', 'imperial', '0.3 mm', True, '0.3 mm', '0 in'),
        ('Lots of small unit', 'imperial', '123456 mm', True, '123456 mm', '405 ft'),
        ('Little of big', 'metric', '0.000001 mi', True, '0 mi', '1.6 mm'),

        ('Do not convert primary unit: metric', 'metric', '10 m', False),
        ('Do not convert primary unit: imperial', 'imperial', '10 ft', False),

        ('Weird unit symbols ft 1', 'metric', '5.5 \'', True, '5.5 ft', '1.7 m'),
        ('Weird unit symbols ft 2', 'metric', '5.5 `', True, '5.5 ft', '1.7 m'),
        ('Weird unit symbols ft 3', 'metric', '5.5 ′', True, '5.5 ft', '1.7 m'),

        ('Weird unit symbols in 1', 'metric', '5.5 "', True, '5.5 in', '14 cm'),
        ('Weird unit symbols in 2', 'metric', '5.5 \'\'', True, '5.5 in', '14 cm'),
        ('Weird unit symbols in 3', 'metric', '5.5 ``', True, '5.5 in', '14 cm'),
        ('Weird unit symbols in 4', 'metric', '5.5 ′′', True, '5.5 in', '14 cm'),
        ('Weird unit symbols in 5', 'metric', '5.5 ″', True, '5.5 in', '14 cm'),

        ('Negative', 'metric', '-5.5 ″', True, '-5.5 in', '-14 cm'),

        # Compound units like 5'11" generally are not supported. But current parsers
        # already half-parse them, treating as 5ft (cutting off inches).
        # So we test to ensure this compatibility remains
        ('Compound ft 1', 'metric', '1\'2"', True, '1 ft', '30.5 cm'),
        ('Compound ft 2', 'metric', '3 ft 4 in', True, '3 ft', '91.4 cm'),
        ('Compound ft 3', 'metric', '5\'6 in', True, '5 ft', '1.5 m'),
        ('Compound ft 4', 'metric', '7 ft8in', True, '7 ft', '2.1 m'),
        ('Compound ft 5', 'metric', '99`1234567', True, '99 ft', '30.2 m'),
    ])
    def testDistanceConverter(
        self, _: str,
        primaryUnitSystem: str,
        text: str, expectSuccess: bool, expectFrom: str | None = None, expectTo: str | None = None,
    ) -> None:
        configOverrides = [
            (ConfigId.Converter_Distance_PrimaryUnit_Metric, True if primaryUnitSystem == 'metric' else False),
        ]

        self.runConverterTest(text, expectSuccess, expectFrom, expectTo, configOverrides)
