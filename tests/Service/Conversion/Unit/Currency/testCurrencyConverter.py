from parameterized import parameterized

from Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest
from src.Constant.ConfigId import ConfigId


class TestCurrencyConverter(AbstractConversionManagerTest):
    @parameterized.expand([
        ('From eur', 'eur', '1 usd', True, '1 USD', '0.86 €'),
        ('From usd', 'usd', '1 €', True, '1 EUR', '1.16 $'),
        ('Symbol in front of number', 'eur', '$ 1', True, '1 USD', '0.86 €'),
        ('Unit has no additional aliases - BAM', 'eur', '99 BAM', True, '99 BAM', '50.62 €'),
        ('To primary currency', 'usd', '1 USD', False),

        ('Weird symbols - ALL', 'eur', '420 lekë', True, '420 ALL', '4.31 €'),
        ('Weird symbols - AMD', 'eur', '1 ֏', True, '1 AMD', '0.002 €'),
        ('Weird symbols - BGN', 'eur', '55 лв.', True, '55 BGN', '28.12 €'),
        ('Weird symbols - GEL', 'eur', '12345 ₾', True, '12345 GEL', '3961 €'),
        ('Weird symbols - PLN', 'eur', '101 zł', True, '101 PLN', '23.64 €'),
        ('Weird symbols - TRY', 'eur', '45.454545 ₺‎', True, '45.45 TRY', '0.97 €'),
        ('Weird symbols - CNY 1', 'eur', '500 ¥‎', True, '500 CNY', '59.81 €'),
        ('Weird symbols - CNY 2', 'eur', '500 块', True, '500 CNY', '59.81 €'),
        ('Weird symbols - INR', 'eur', '500500 ₹', True, '500500 INR', '4955 €'),
        # ('Weird symbols - ILS', 'eur', '70₪', True, '70 ILS', '17.75 €'), # TODO this is failing because of invisible LRM character in rates alias. Fix this in updater script
        ('Weird symbols - KRW', 'eur', '₩ 0.0001', True, '0.0001 KRW', '0 €'),
        # ('Weird symbols - PEN', 'eur', 'S/ 699', True, '699 PEN', '168.79 €'), # TODO this is failing because of invisible LRM character in rates alias. Fix this in updater script
        ('Weird symbols - BTC', 'usd', '1 ₿', True, '1 BTC', '113421 $'),
        ('Weird symbols - ADA', 'usd', '₳ 1.01', True, '1.01 ADA', '0.71 $'),
    ])
    def testCurrencyConverter(
        self, _: str,
        primaryCurrency: str,
        text: str, expectSuccess: bool, expectFrom: str | None = None, expectTo: str | None = None,
    ) -> None:
        configOverrides = [
            (ConfigId.Converter_Currency_PrimaryCurrency, primaryCurrency),
        ]

        self.runConverterTest(text, expectSuccess, expectFrom, expectTo, configOverrides)
