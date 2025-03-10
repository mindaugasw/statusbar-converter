from unittest.mock import patch

from parameterized import parameterized

from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestConversionManager(AbstractConversionManagerTest):
    @parameterized.expand([
        ('None', None, False, None, None),
        ('Empty string', '', False, None, None),
        ('Random text', 'Random text', False, None, None),
        ('No matched converter', '123 asd', False, None, None),
        ('Timestamp converter', '1555522011', True, '1555522011', '1555522011'),
        ('Temperature converter', '15 F', True, '15 °F', '-9 °C'),
        ('Distance converter', '15 ft', True, '15 ft', '4.6 m'),
        ('Volume converter', '15 floz', True, '15 fl oz', '507.2 ml'),
        ('Weight converter', '15 lb', True, '15 lb', '6.8 kg'),

        # Edge cases
        ('Negative', '-15 lb', True, '-15 lb', '-6.8 kg'),

        ('Whitespace - no whitespace', '5.5″', True, '5.5 in', '14 cm'),
        ('Whitespace - everything', '- \n \r 5.5 \t \r\n ″', True, '-5.5 in', '-14 cm'),

        ('Letter case - uppercase', '5.5 FT', True, '5.5 ft', '1.7 m'),
        ('Letter case - different', '5.5 fT', True, '5.5 ft', '1.7 m'),
    ])
    @patch('time.time', return_value=1733022011.42)
    def testConversionManagerGeneral(
        self, _: str,
        text: str, expectSuccess: bool, expectFrom: str | None, expectTo: str | None,
        timeMock,
    ) -> None:
        self.runConverterTest(text, expectSuccess, expectFrom, expectTo)
