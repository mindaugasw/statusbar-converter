import re

from src.Constant.Logs import Logs
from src.DTO.ConvertResult import ConvertResult
from src.DTO.Timestamp import Timestamp
from src.Service.Configuration import Configuration
from src.Service.Converter.ConverterInterface import ConverterInterface
from src.Service.Logger import Logger
from src.Service.TimestampTextFormatter import TimestampTextFormatter


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
    _config: Configuration
    _logger: Logger

    def __init__(self, formatter: TimestampTextFormatter, config: Configuration, logger: Logger):
        self._formatter = formatter
        self._config = config
        self._logger = logger

    def getConverterName(self) -> str:
        return 'Timestamp'

    def tryConvert(self, content: str) -> (bool, ConvertResult | None):
        timestamp = self._extractTimestamp(content)

        if timestamp is None:
            return False, None

        templateOriginalText = self._config.get(Configuration.MENU_ITEMS_LAST_CONVERSION_ORIGINAL_TEXT)
        templateConvertedText = self._config.get(Configuration.MENU_ITEMS_LAST_CONVERSION_CONVERTED_TEXT)

        return (
            True,
            ConvertResult(
                self._formatter.formatForIcon(timestamp),
                self._formatter.format(timestamp, templateOriginalText),
                self._formatter.format(timestamp, templateConvertedText),
            ),
        )

    def _extractTimestamp(self, content: str) -> Timestamp | None:
        regexResult = re.match(self.REGEX_PATTERN, content)

        if regexResult is None:
            return None

        try:
            number = int(content)
        except Exception as e:
            self._logger.logDebug(
                f'{Logs.catConverter}{self.getConverterName()}] '
                f'Exception occurred while converting copied text to integer.\n'
                f'Copied content: {content}\n'
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
