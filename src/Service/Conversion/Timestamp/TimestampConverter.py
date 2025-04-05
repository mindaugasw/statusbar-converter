import re
from typing import Tuple, Final

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Timestamp import Timestamp
from src.Service.Configuration import Configuration
from src.Service.Conversion.ConverterInterface import ConverterInterface
from src.Service.Conversion.Timestamp.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Logger import Logger


class TimestampConverter(ConverterInterface):
    _REGEX_PATTERN: Final[str] = '^\\d{1,14}$'
    _MIN_VALUE: Final[int] = 100000000  # 1973-03-03
    _MAX_VALUE: Final[int] = 9999999999  # 2286-11-20

    _MILLIS_MIN_CHARACTERS: Final[int] = 12
    _MILLIS_MAX_CHARACTERS: Final[int] = 14
    """
    If a number has between MILLIS_MIN_CHARACTERS and MILLIS_MAX_CHARACTERS digits,
    it will be considered a millisecond timestamp. Otherwise a regular timestamp.
    """

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

    def tryConvert(self, text: str) -> Tuple[bool, ConvertResult | None]:
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
        regexResult = re.match(self._REGEX_PATTERN, text)

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

        if self._MILLIS_MIN_CHARACTERS <= len(numberString) <= self._MILLIS_MAX_CHARACTERS:
            seconds = int(numberString[:-3])
            milliseconds = int(numberString[-3:])
        else:
            seconds = number
            milliseconds = None

        if self._MIN_VALUE <= seconds <= self._MAX_VALUE:
            return Timestamp(seconds, milliseconds)

        return None
