import re

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Timestamp import Timestamp
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Conversion.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Logger import Logger


class TimestampConverter(ConverterInterface):
    REGEX_PATTERN = '^\\d{1,14}$'
    MIN_VALUE = 100000000  # 1973-03-03
    MAX_VALUE = 9999999999  # 2286-11-20
    """
    If a number has between MILLIS_MIN_CHARACTERS and MILLIS_MAX_CHARACTERS digits,
    it will be considered a millisecond timestamp. Otherwise a regular timestamp.
    """
    MILLIS_MIN_CHARACTERS = 12
    MILLIS_MAX_CHARACTERS = 14

    _formatter: TimestampTextFormatter
    _logger: Logger

    _enabled: bool
    _templateOriginalText: str
    _templateConvertedText: str

    def __init__(self, formatter: TimestampTextFormatter, config: Configuration, logger: Logger):
        self._formatter = formatter
        self._logger = logger

        self._enabled = config.get(ConfigId.Converter_Timestamp_Enabled)
        self._templateOriginalText = config.get(ConfigId.Converter_Timestamp_Menu_LastConversion_OriginalText)
        self._templateConvertedText = config.get(ConfigId.Converter_Timestamp_Menu_LastConversion_ConvertedText)

    def isEnabled(self) -> bool:
        return self._enabled

    def getName(self) -> str:
        return 'Timestamp'

    def tryConvert(self, text: str) -> (bool, ConvertResult | None):
        timestamp = self._extractTimestamp(text)

        if timestamp is None:
            return False, None

        return (
            True,
            ConvertResult(
                self._formatter.formatForIcon(timestamp),
                self._formatter.format(timestamp, self._templateOriginalText),
                self._formatter.format(timestamp, self._templateConvertedText),
                self.getName(),
            ),
        )

    def _extractTimestamp(self, text: str) -> Timestamp | None:
        regexResult = re.match(self.REGEX_PATTERN, text)

        if regexResult is None:
            return None

        try:
            number = int(text)
        except Exception as e:
            self._logger.logDebug(
                f'{Logs.catConverter}{self.getName()}] '
                f'Exception occurred while converting copied text to integer.\n'
                f'Copied content: {text}\n'
                f'Exception: {type(e)}\n'
                f'Message: {str(e)}'
            )

            return None

        numberString = str(number)

        if self.MILLIS_MIN_CHARACTERS <= len(numberString) <= self.MILLIS_MAX_CHARACTERS:
            seconds = int(numberString[:-3])
            milliseconds = int(numberString[-3:])
        else:
            seconds = number
            milliseconds = None

        if self.MIN_VALUE <= seconds <= self.MAX_VALUE:
            return Timestamp(seconds, milliseconds)

        return None
