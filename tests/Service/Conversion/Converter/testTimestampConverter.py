from unittest.mock import patch

from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from tests.Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest


class TestTimestampConverter(AbstractConversionManagerTest):
    @parameterized.expand([
        ('Empty string', '', False, None),
        ('Random text', 'Random text', False, None),
        ('Valid timestamp', '1555522011', True, '1555522011'),
        ('Millisecond timestamp', '1555522011123', True, '1555522011.123'),
        ('Millisecond timestamp with a dot', '1555522011.123', False, None),
        ('8 chars: below min value', '12345678', False, None),
        ('9 chars: min value', '123456789', True, '123456789'),
        ('10 chars: regular timestamp', '1234567890', True, '1234567890'),
        ('10 chars: max value', '9999999999', True, '9999999999'),
        ('11 chars: too long for seconds', '12345678901', False, None),
        ('12 chars: min value, ms', '100000000000', True, '100000000.000'),
        ('13 chars: regular timestamp, ms', '1234567890123', True, '1234567890.123'),
        ('14 chars: max value, ms', '9999999999999', True, '9999999999.999'),
        ('15 chars: too long for ms', '10000000000000', False, None),
    ])
    @patch('time.time', return_value=1733022011.42)
    def testTimestampConverter(
        self, _: str,
        text: str, expectSuccess: bool, expectParsed: str | None,
        timeMock,
    ) -> None:
        configOverrides = [
            (ConfigId.Converter_Timestamp_Menu_LastConversion_OriginalText, '{ts_ms_sep}'),
            (ConfigId.Converter_Timestamp_Menu_LastConversion_ConvertedText, '{ts_ms_sep}'),
        ]

        self.runConverterTest(text, expectSuccess, expectParsed, expectParsed, configOverrides)
