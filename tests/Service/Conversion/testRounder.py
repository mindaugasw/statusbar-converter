from parameterized import parameterized

from src.Service.Conversion.Rounder import Rounder
from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestRounder(AbstractConversionManagerTest):
    @parameterized.expand([
        ('Distance min', '0.00413701 in', '0.0041 in', '0.11 mm'),
        ('Distance 2', '1.1234567890123456 in', '1.12 in', '2.85 cm'),
        ('Distance max', '621370.570 mi', '621371 mi', '999999 km'),

        # Temperature - ok as is (round to int), without custom rounding
        ('Temperature min', '0.0000000000123456 F', '0 °F', '-18 °C'),
        ('Temperature 2', '1.1234567890123456 F', '1 °F', '-17 °C'),
        ('Temperature 3', '52.5 F', '52 °F', '11 °C'),
        ('Temperature max', '999999 F', '999999 °F', '555537 °C'),

        ('Volume min', '0.0033814 fl oz', '0.0034 fl oz', '0.11 ml'),
        ('Volume 2', '0.033814 fl oz', '0.034 fl oz', '1.14 ml'),
        ('Volume 3', '0.33814 fl oz', '0.34 fl oz', '11.4 ml'),
        ('Volume 4', '3.3814 fl oz', '3.38 fl oz', '114 ml'),

        ('Weight min', '0.0000035274 oz', '0 oz', '0.1 mg'),
        ('Weight 1', '0.000035274 oz', '0.00004 oz', '1 mg'),
        ('Weight 2', '0.0035274 oz', '0.0035 oz', '100 mg'),
        ('Weight 3', '3.5274 oz', '3.53 oz', '100 g'),
        ('Weight 4', '35.27486 oz', '35.3 oz', '1 kg'),
        ('Weight 5', '352.7486 oz', '353 oz', '10 kg'),

        ('Currency 1', '0.0001234 usd', '0.0001 USD', '0.0001 €'),
        ('Currency 2', '0.0012345 usd', '0.001 USD', '0.001 €'),
        ('Currency 3', '0.0123456 usd', '0.01 USD', '0.01 €'),
        ('Currency 4', '1.1234567 usd', '1.12 USD', '0.97 €'),
        ('Currency 5', '11.234567 usd', '11.23 USD', '9.69 €'),
        ('Currency 6', '112.34567 usd', '112.35 USD', '96.9 €'),
        ('Currency 7', '1123.4567 usd', '1123 USD', '969.04 €'),
    ])
    def testRounderIntegration(
        self, _: str,
        text: str, expectFrom: str, expectTo: str,
    ) -> None:
        self.runConverterTest(text, True, expectFrom, expectTo)

    @parameterized.expand([
        ('regular', 0, '0'),
        ('regular', 0.0000001, '0'),
        ('regular', 0.000001, '0'),
        ('regular', 0.00001, '0.00001'),
        ('regular', 0.00001234, '0.00001'),
        ('regular', 0.00001999, '0.00002'),
        ('regular', 0.0001, '0.0001'),
        ('regular', 0.000101, '0.0001'),
        ('regular', 0.001, '0.001'),
        ('regular', 0.00101, '0.001'),
        ('regular', 0.013, '0.013'),
        ('regular', 0.012345, '0.012'),
        ('regular', 0.123456, '0.12'),
        ('regular', 1.234567, '1.23'),
        ('regular', 12.34567, '12.3'),
        ('regular', 123.4567, '123'),
        ('regular', 12345.67, '12346'),
        ('regular', -0, '0'),
        ('regular', -0.0000001, '0'),
        ('regular', -0.0015, '-0.0015'),
        ('regular', -0.1, '-0.1'),
        ('regular', -1.2, '-1.2'),
        ('regular', -10.55, '-10.6'),
        ('regular', -111.123456, '-111'),
        ('currency', 0.00001, '0.00001'),
        ('currency', 0.0001, '0.0001'),
        ('currency', 0.001, '0.001'),
        ('currency', 0.01, '0.01'),
        ('currency', 0.1, '0.1'),
        ('currency', 1.556745, '1.56'),
        ('currency', 15.56745, '15.57'),
        ('currency', 155.6745, '155.67'),
        ('currency', 1556.745, '1557'),
    ])
    def testRounderUnit(self, method: str, number: float, expected: str) -> None:
        rounder = Rounder()

        if method == 'regular':
            result = rounder.round(number)
        elif method == 'currency':
            result = rounder.roundCurrency(number)
        else:
            raise Exception('Unknown rounder method')

        self.assertEqual(expected, result)
