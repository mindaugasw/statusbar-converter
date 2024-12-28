from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.DTO.Timestamp import Timestamp
from src.Service.Conversion.Converter.Timestamp.TimestampTextFormatter import TimestampTextFormatter
from tests.TestUtil.MockLibrary import MockLibrary


class TestTimestampTextFormatter(TestCase):

    @parameterized.expand([
        ('Generic datetime', 1733021011, None, '%Y-%m-%d %H:%M:%S', '2024-12-01 04:43:31'),
        ('Custom formats, without ms', 1733021011, None, '{ts}, {ts_ms}, {ts_ms_sep}', '1733021011, 1733021011, 1733021011'),
        ('Custom formats, with ms', 1733021011, 543, '{ts}, {ts_ms}, {ts_ms_sep}', '1733021011, 1733021011543, 1733021011.543'),
        ('Seconds ago', 1733022011 - 30, None, '{r_int}, {r_float}', '30 s ago, 30.0 s ago'),
        ('Minutes ago', 1733022011 - 30 * 60 - 15, 444, '{r_int}, {r_float}', '30 min ago, 30.2 min ago'),
        ('Hours ago', 1733022011 - 3600 * 2.5, None, '{r_int}, {r_float}', '2 h ago, 2.5 h ago'),
        ('Days ago', 1733022011 - 3600 * 24 * 2.3671, 771, '{r_int}, {r_float}', '2 days ago, 2.4 days ago'),
        ('Months ago', 1733022011 - 3600 * 24 * 200.3671, None, '{r_int}, {r_float}', '6 months ago, 6.5 months ago'),
        ('Years ago', 1733022011 - 3600 * 24 * 365 * 15.111, None, '{r_int}, {r_float}', '15 years ago, 15.1 years ago'),
        ('In seconds', 1733022011 + 15, None, '{r_int}, {r_float}', 'in 15 s, in 15.0 s'),
        ('In years', 1733022011 + 3600 * 24 * 365 * 15.111, None, '{r_int}, {r_float}', 'in 15 years, in 15.1 years'),
    ])
    @patch('time.time', return_value=1733022011.42)
    def testFormat(
        self, _: str,
        seconds: int, milliseconds: int | None, template: str,
        expected: str,
        timeMock,
    ) -> None:
        configMock = MockLibrary.getConfig([
            (ConfigId.Converter_Timestamp_IconFormat, {}),
        ])
        formatter = TimestampTextFormatter(configMock)

        text = formatter.format(Timestamp(seconds, milliseconds), template)

        self.assertEqual(expected, text)

    @parameterized.expand([
        ('Level 4', 1733022011 - 86400 + 100, 'none 4'),
        ('Level 5', 1733022011 - 86400 - 100, '1732935511 - 1.0 days ago (11-30  04:58)'),
        ('Level 6', 1733022011 - 2678400 - 100, 'none 6'),
        ('Level default', 1733022011 + 2365200000 + 100, '4098222111 - in 75.0 years'),
    ])
    @patch('time.time', return_value=1733022011.42)
    def testFormatForIcon(self, _: str, seconds: int, expected: str, timeMock) -> None:
        configMock = MockLibrary.getConfig([
            (ConfigId.Converter_Timestamp_IconFormat, {
                '60': 'none 1',
                '600': 'none 2',
                '3600': 'none 3',
                '86400': 'none 4',
                '2678400': '{ts_ms_sep} - {r_float} (%m-%d  %H:%M)',
                '31536000': 'none 6',
                '2365200000': 'none 7',
                'default': '{ts_ms_sep} - {r_float}',
            }),
        ])
        formatter = TimestampTextFormatter(configMock)

        text = formatter.formatForIcon(Timestamp(seconds, None))

        self.assertEqual(expected, text)
