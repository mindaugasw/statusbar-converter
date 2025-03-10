from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestWeightConverter(AbstractConversionManagerTest):
    @parameterized.expand([
        ('To mg', 'metric', '0.003 oz', True, '0 oz', '85 mg'),
        ('To g', 'metric', '3 oz.', True, '3 oz', '85 g'),
        ('To kg', 'metric', '4.5 lbs', True, '4.5 lb', '2 kg'),
        ('From stone', 'metric', '4.5 st', True, '4.5 st', '28.6 kg'),
        ('To metric tonne', 'metric', '12 ton', True, '12 t', '12192.6 kg'),

        ('To ounce', 'imperial', '30 g', True, '30 g', '1.1 oz'),
        ('To pound', 'imperial', '30 kg', True, '30 kg', '66.1 lb'),
        ('To imperial ton', 'imperial', '12 tonne', True, '12 t', '26455.5 lb'),

        ('Negative', 'metric', '4.5 lbs', True, '4.5 lb', '2 kg'),
    ])
    def testWeightConverter(
        self, _: str,
        primaryUnitSystem: str,
        text: str, expectSuccess: bool, expectFrom: str | None = None, expectTo: str | None = None,
    ) -> None:
        configOverrides = [
            (ConfigId.Converter_Weight_PrimaryUnit_Metric, True if primaryUnitSystem == 'metric' else False),
        ]

        self.runConverterTest(text, expectSuccess, expectFrom, expectTo, configOverrides)
