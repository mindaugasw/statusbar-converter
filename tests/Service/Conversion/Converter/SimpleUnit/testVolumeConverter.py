from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.Service.Conversion.Converter.SimpleUnit.VolumeConverter import VolumeConverter
from tests.Service.Conversion.Converter.SimpleUnit.AbstractSimpleUnitConverterTest import \
    AbstractSimpleUnitConverterTest
from tests.TestUtil.MockLibrary import MockLibrary


class TestVolumeConverter(AbstractSimpleUnitConverterTest):
    @parameterized.expand([
        ('To mm3, too small number', 0.0029, 'floz', 'metric', False),
        ('To mm3', 0.0035, 'floz', 'metric', True, '0 fl oz', '118.3 mm3'),
        ('To ml', 0.035, 'floz', 'metric', True, '0 fl oz', '1.2 ml'),
        ('To cl/dl (unit skipped)', 10, 'floz', 'metric', True, '10 fl oz', '338.1 ml'),
        ('To l', 5, 'gal', 'metric', True, '5 gal', '1.3 l'),
        ('To m3 (unit skipped)', 7922, 'gal', 'metric', True, '7922 gal', '2092.8 l'),

        ('To fl oz', 80, 'ml', 'imperial', True, '80 ml', '2.4 fl oz'),
        ('To gal', 80, 'l', 'imperial', True, '80 l', '302.8 gal'),
    ])
    def testConversion(
        self, _: str,
        number: float, unitId: str, primaryUnitSystem: str,
        expectedSuccess: bool, expectedFrom: str | None = None, expectedTo: str | None = None,
    ):
        configMock = MockLibrary.getConfig([
            (ConfigId.Converter_Volume_Enabled, True),
            (ConfigId.Converter_Volume_PrimaryUnit_Metric, True if primaryUnitSystem == 'metric' else False),
        ])
        converter = VolumeConverter(configMock)

        self._testTryConvert(converter, number, unitId, expectedSuccess, expectedFrom, expectedTo)
