from unittest import TestCase

from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.Service.Conversion.Converter.SimpleUnit.WeightConverter import WeightConverter
from tests.TestUtil.MockLibrary import MockLibrary


class TestWeightConverter(TestCase):
    @parameterized.expand([
        ('To mg', 0.003, 'oz', 'metric', True, '0 oz', '85 mg'),
        ('To g', 3, 'oz.', 'metric', True, '3 oz', '85 g'),
        ('To kg', 4.5, 'lbs', 'metric', True, '4.5 lb', '2 kg'),
        ('From stone', 4.5, 'st', 'metric', True, '4.5 st', '28.6 kg'),
        ('To metric tonne', 12, 'ton', 'metric', True, '12 t', '12192.6 kg'),

        ('To ounce', 30, 'g', 'imperial', True, '30 g', '1.1 oz'),
        ('To pound', 30, 'kg', 'imperial', True, '30 kg', '66.1 lb'),
        ('To imperial ton', 12, 'tonne', 'imperial', True, '12 t', '26455.5 lb'),
    ])
    def testTryConvert(
        self, _: str,
        number: float, unitId: str, primaryUnitSystem: str,
        expectedSuccess: bool, expectedFrom: str | None = None, expectedTo: str | None = None,
    ) -> None:
        if unitId != unitId.lower():
            raise Exception('tryConvert function expects already lower-cased unitId')

        configMock = MockLibrary.getConfig([
            (ConfigId.Converter_Weight_Enabled, True),
            (ConfigId.Converter_Weight_PrimaryUnit_Metric, True if primaryUnitSystem == 'metric' else False)
        ])

        converter = WeightConverter(configMock)

        success, result = converter.tryConvert(number, unitId)

        self.assertEqual(expectedSuccess, success)

        if success:
            self.assertEqual(expectedFrom, result.originalText)
            self.assertEqual(expectedTo, result.convertedText)
