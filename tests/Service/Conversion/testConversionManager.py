from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from parameterized import parameterized

from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Conversion.ConversionManager import ConversionManager
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.SimpleUnitConverter import SimpleUnitConverter
from src.Service.Conversion.Converter.SimpleUnit.TemperatureConverter import TemperatureConverter
from src.Service.Conversion.Converter.SimpleUnit.UnitPreprocessor import UnitPreprocessor
from src.Service.Conversion.Converter.TimestampConverter import TimestampConverter
from src.Service.Conversion.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Debug import Debug
from src.Service.EventService import EventService
from src.Service.Logger import Logger
from tests.TestUtil.MockLibrary import MockLibrary


class TestConversionManager(TestCase):
    _events: EventService

    _convertedWasDispatched: bool
    _convertResult : ConvertResult | None

    def setUp(self) -> None:
        self._events = EventService()
        self._convertedWasDispatched = False
        self._convertResult = None

    @parameterized.expand([
        ('Empty string', '', False, None),
        ('Random text', 'Random text', False, None),
        ('No matched converter', '123 asd', False, None),
        ('Timestamp converter', '1555522011', True, '1555522011'),
        ('Temperature converter', '15 F', True, '-9 °C'),
    ])
    @patch('time.time', return_value=1733022011.42)
    def testOnClipboardChange(
        self, _: str,
        text: str, expectSuccess: bool, expectText: str | None,
        timeMock,
    ) -> None:
        def onConverted(result: ConvertResult) -> None:
            self._convertedWasDispatched = True
            self._convertResult = result

        self._events.subscribeConverted(onConverted)
        conversionManager = self._buildConversionManager()

        conversionManager.onClipboardChange(text)

        self.assertEqual(expectSuccess, self._convertedWasDispatched)

        if expectSuccess:
            self.assertEqual(expectText, self._convertResult.convertedText)

    def _buildConversionManager(self) -> ConversionManager:
        loggerMock = Mock(Logger)
        configMock = MockLibrary.getConfig([
            (ConfigId.ClearOnChange, False),
            (ConfigId.ClearAfterTime, 0),
            (ConfigId.Debug, False),
            (ConfigId.Converter_Timestamp_Enabled, True),
            (ConfigId.Converter_Timestamp_IconFormat, {'default': ''}),
            (ConfigId.Converter_Timestamp_Menu_LastConversion_OriginalText, ''),
            (ConfigId.Converter_Timestamp_Menu_LastConversion_ConvertedText, '{ts_ms_sep}'),
            (ConfigId.Converter_Temperature_Enabled, True),
            (ConfigId.Converter_Temperature_PrimaryUnit, 'C'),
        ])

        simpleConverters: list[SimpleConverterInterface] = [
            TemperatureConverter(
                UnitPreprocessor(),
                configMock,
            ),
        ]

        converters: list[ConverterInterface] = [
            TimestampConverter(
                TimestampTextFormatter(configMock),
                configMock,
                loggerMock,
            ),
            SimpleUnitConverter(
                simpleConverters,
                ThousandsDetector(),
            ),
        ]

        argParserMock = MagicMock(ArgumentParser)
        argParserMock.isDebugEnabled.return_value = False
        argParserMock.getMockUpdate.return_value = None

        conversionManager = ConversionManager(
            converters,
            self._events,
            configMock,
            loggerMock,
            Debug(
                configMock,
                argParserMock,
            ),
        )

        return conversionManager
