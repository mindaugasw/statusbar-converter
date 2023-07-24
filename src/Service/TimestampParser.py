import re
import time
import src.events as events
from src.Service import Configuration
from src.Service.Debug import Debug
from src.Entity.Timestamp import Timestamp


class TimestampParser:
    REGEX_PATTERN = '^\\d{1,14}$'
    MIN_VALUE = 100000000  # 1973-03-03
    MAX_VALUE = 9999999999  # 2286-11-20
    MILLIS_MIN_CHARACTERS = 12
    """
    If a number has between MILLIS_MIN_CHARACTERS and MILLIS_MAX_CHARACTERS digits,
    it will be considered millisecond timestamp. Otherwise regular timestamp.
    """
    MILLIS_MAX_CHARACTERS = 14

    _debug: Debug
    _clearOnChange: bool
    _clearAfterTime: int
    _timestampSetAt: int | None = None

    def __init__(self, config: Configuration, debug: Debug):
        self._debug = debug

        self._clearOnChange = config.get(config.CLEAR_ON_CHANGE)
        self._clearAfterTime = config.get(config.CLEAR_AFTER_TIME)

        events.clipboardChanged.append(self._processChangedClipboard)
        events.timestampChanged.append(self._onTimestampChanged)
        events.timestampClear.append(self._onTimestampClear)
        events.appLoopIteration.append(self._clearTimestampAfterTime)

    def _processChangedClipboard(self, content: str) -> None:
        timestamp = self._extractTimestamp(content)

        if timestamp is None:
            if self._clearOnChange and self._timestampSetAt:
                events.timestampClear()

            return

        events.timestampChanged(timestamp)

    def _extractTimestamp(self, content: str) -> Timestamp | None:
        regexResult = re.match(TimestampParser.REGEX_PATTERN, content)

        if regexResult is None:
            return None

        try:
            number = int(content)
        except Exception as e:
            self._debug.log(
                f'Exception occurred while converting copied text to integer.\n'
                f'Copied content: {content}\n'
                f'Exception: {type(e)}\n'
                f'Exception message: {str(e)}'
            )

            return None

        numberString = str(number)

        if TimestampParser.MILLIS_MIN_CHARACTERS <= len(numberString) <= TimestampParser.MILLIS_MAX_CHARACTERS:
            seconds = int(numberString[:-3])
            milliseconds = int(numberString[-3:])
        else:
            seconds = number
            milliseconds = None

        if TimestampParser.MIN_VALUE <= seconds <= TimestampParser.MAX_VALUE:
            return Timestamp(seconds, milliseconds)

        return None

    def _onTimestampChanged(self, timestamp: Timestamp) -> None:
        self._timestampSetAt = int(time.time())

    def _onTimestampClear(self) -> None:
        self._timestampSetAt = None

    def _clearTimestampAfterTime(self) -> None:
        if self._clearAfterTime <= 0 or not self._timestampSetAt:
            return

        if int(time.time()) - self._timestampSetAt < self._clearAfterTime:
            return

        self._debug.log('Auto clearing timestamp after timeout')
        events.timestampClear()
