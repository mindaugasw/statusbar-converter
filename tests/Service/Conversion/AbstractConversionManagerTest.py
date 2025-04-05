from unittest import TestCase
from unittest.mock import Mock, MagicMock

from src.Constant.ConfigId import ConfigId
from src.DTO.ConvertResult import ConvertResult
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Conversion.ConversionManager import ConversionManager
from src.Service.Conversion.Timestamp.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Debug import Debug
from src.Service.EventService import EventService
from src.Service.Logger import Logger
from src.Service.ServiceContainer import ServiceContainer
from tests.TestUtil.MockLibrary import MockLibrary
from tests.TestUtil.Types import ConfigurationsList


class AbstractConversionManagerTest(TestCase):
    # All converters are tested with a single integration test to ensure proper service config.
    # E.g. test that SimpleUnitConverter has correct regex, that multiple converters are not clashing, etc

    _events: EventService

    _convertedWasDispatched: bool
    _convertResult: ConvertResult | None

    def setUp(self) -> None:
        def onConverted(result: ConvertResult) -> None:
            self._convertedWasDispatched = True
            self._convertResult = result

        self._convertedWasDispatched = False
        self._convertResult = None
        self._events = EventService()
        self._events.subscribeConverted(onConverted)

    def runConverterTest(
        self,
        text: str | None, expectSuccess: bool, expectFrom: str | None, expectTo: str | None,
        configOverrides: ConfigurationsList | None = None,
    ) -> None:
        if text is not None and text != text.strip():
            raise Exception('This service should always receive only whitespace-stripped input')

        conversionManager = self.buildConversionManager(configOverrides)

        conversionManager.onClipboardChange(text)

        self.assertConvertResult(expectSuccess, expectFrom, expectTo)


    def assertConvertResult(self, expectSuccess: bool, expectFrom: str | None = None, expectTo: str | None = None) -> None:
        self.assertEqual(
            expectSuccess,
            self._convertedWasDispatched,
            f'Expected convert success {expectSuccess}, got success {self._convertedWasDispatched}',
        )

        if expectSuccess:
            self.assertEqual(expectFrom, self._convertResult.originalText)  # type: ignore[union-attr]
            self.assertEqual(expectTo, self._convertResult.convertedText)  # type: ignore[union-attr]

    def buildConversionManager(self, configOverrides: ConfigurationsList | None = None) -> ConversionManager:
        configDefault = [
            (ConfigId.ClearOnChange, False),
            (ConfigId.ClearAfterTime, 0),
            (ConfigId.Debug, False),
            (ConfigId.Converter_Distance_Enabled, True),
            (ConfigId.Converter_Distance_PrimaryUnit_Metric, True),
            (ConfigId.Converter_Temperature_Enabled, True),
            (ConfigId.Converter_Temperature_PrimaryUnit_Celsius, True),
            (ConfigId.Converter_Timestamp_Enabled, True),
            (ConfigId.Converter_Timestamp_IconFormat, {'default': ''}),
            (ConfigId.Converter_Timestamp_Menu_LastConversion_OriginalText, '{ts_ms_sep}'),
            (ConfigId.Converter_Timestamp_Menu_LastConversion_ConvertedText, '{ts_ms_sep}'),
            (ConfigId.Converter_Volume_Enabled, True),
            (ConfigId.Converter_Volume_PrimaryUnit_Metric, True),
            (ConfigId.Converter_Weight_Enabled, True),
            (ConfigId.Converter_Weight_PrimaryUnit_Metric, True),
        ]

        argParserMock = MagicMock(ArgumentParser)
        argParserMock.isDebugEnabled.return_value = False
        argParserMock.getMockUpdate.return_value = None

        configMock = MockLibrary.getConfig(configDefault, configOverrides)
        loggerMock = Mock(Logger)
        debugMock = Debug(configMock, argParserMock)

        timestampTextFormatter = TimestampTextFormatter(configMock)

        conversionManager = ServiceContainer().getConversionManager(
            timestampTextFormatter,
            configMock,
            loggerMock,
            self._events,
            debugMock,
        )

        return conversionManager
