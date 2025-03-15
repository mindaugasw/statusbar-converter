from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestVolumeConverter(AbstractConversionManagerTest):
    @parameterized.expand([
        ('To mm3, too small number', 'metric', '0.0029 floz', False),
        ('To mm3', 'metric', '0.0035 floz', True, '0 fl oz', '118.3 mm3'),
        ('To ml', 'metric', '0.035 floz', True, '0 fl oz', '1.2 ml'),
        ('To cl/dl (unit skipped)', 'metric', '10 floz', True, '10 fl oz', '338.1 ml'),
        ('To l', 'metric', '5 gal', True, '5 gal', '1.3 l'),
        ('To m3 (unit skipped)', 'metric', '7922 gal', True, '7922 gal', '2092.8 l'),
        ('From tbsp', 'metric', '3.5 tbsp.', True, '3.5 tbsp', '51.8 ml'),
        ('From tsp', 'metric', '2 tsp', True, '2 tsp', '9.9 ml'),

        ('To fl oz', 'imperial', '80 ml', True, '80 ml', '2.4 fl oz'),
        ('To gal', 'imperial', '80 l', True, '80 l', '302.8 gal'),

        ('Negative', 'metric', '-5 gal', True, '-5 gal', '-1.3 l'),
    ])
    def testVolumeConverter(
        self, _: str,
        primaryUnitSystem: str,
        text: str, expectSuccess: bool, expectFrom: str | None = None, expectTo: str | None = None,
    ):
        configOverrides = [
            (ConfigId.Converter_Volume_PrimaryUnit_Metric, True if primaryUnitSystem == 'metric' else False),
        ]

        self.runConverterTest(text, expectSuccess, expectFrom, expectTo, configOverrides)
