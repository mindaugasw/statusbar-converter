import random
import re
import threading
import time
import src.events as events
from src.Service import Configuration
from src.Service.Debug import Debug
from src.Entity.Timestamp import Timestamp


class TimestampParser:
    REGEX_PATTERN = '^\\d{1,14}$'
    MILLIS_MIN_CHARACTERS = 12
    """
    If a number has between MILLIS_MIN_CHARACTERS and MILLIS_MAX_CHARACTERS digits,
    it will be considered millisecond timestamp. Otherwise regular timestamp.
    """
    MILLIS_MAX_CHARACTERS = 14
    AUTO_CLEAR_SLEEP_INTERVAL = 5
    """
    If configuration to automatically clear timestamp after time is enabled,
    this defines interval in seconds between auto clear checks
    """

    _debug: Debug
    _minValue: int
    _maxValue: int
    _clearOnChange: bool
    _clearAfterTime: int
    _lastTimestampId: int
    """
    Randomly assigned ID, changes for each timestamp.
    Used to check if timestamp didn't change before automatically clearing it
    """
    _timestampSet = False
    _skipTimestamp: str | None = None

    def __init__(self, config: Configuration, debug: Debug):
        self._debug = debug

        self._minValue = config.get(config.TIMESTAMP_MIN)
        self._maxValue = config.get(config.TIMESTAMP_MAX)
        self._clearOnChange = config.get(config.CLEAR_ON_CHANGE)
        self._clearAfterTime = config.get(config.CLEAR_AFTER_TIME)

        events.clipboardChanged.append(self._process)
        events.timestampChanged.append(self._onTimestampChanged)
        events.timestampCleared.append(self._onTimestampCleared)

    def skipNextTimestamp(self, timestamp: str) -> None:
        """Set next expected timestamp value that should be ignored and not parsed

        Can be used to intentionally ignore timestamp when it was set by the
        application itself
        """

        self._skipTimestamp = timestamp

    def _process(self, content: str) -> None:
        if self._skipTimestamp == content:
            self._skipTimestamp = None

            return

        timestamp = self._extractTimestamp(content)

        if timestamp is None:
            if self._clearOnChange and self._timestampSet:
                events.timestampCleared()

            return

        events.timestampChanged(timestamp)

    def _extractTimestamp(self, content: str) -> Timestamp | None:
        content = content.strip()
        regexResult = re.match(self.REGEX_PATTERN, content)

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

        numberStr = str(number)

        if self.MILLIS_MIN_CHARACTERS <= len(numberStr) <= self.MILLIS_MAX_CHARACTERS:
            seconds = int(numberStr[:-3])
            milliseconds = int(numberStr[-3:])
        else:
            seconds = number
            milliseconds = None

        if self._minValue <= seconds <= self._maxValue:
            return Timestamp(seconds, milliseconds)

        return None

    def _onTimestampChanged(self, timestamp: Timestamp) -> None:
        self._timestampSet = True

        if self._clearAfterTime > 0:
            self._lastTimestampId = random.randint(0, 999999)
            threading.Thread(target=self._clearTimestampAfterTime).start()

    def _onTimestampCleared(self) -> None:
        self._timestampSet = False

    def _clearTimestampAfterTime(self) -> None:
        # This is used as a stop flag - if _lastTimestampId changes during
        # thread's lifetime, that means timestamp has updated and this thread
        # should exit early without clearing new timestamp - a new thread was
        # created for that with new countdown
        initialTimestampId = self._lastTimestampId
        threadStartedAt = int(time.time())
        self._debug.log(f'Auto clear - starting thread #{initialTimestampId}')

        while int(time.time()) - threadStartedAt < self._clearAfterTime:
            time.sleep(self.AUTO_CLEAR_SLEEP_INTERVAL)

            if initialTimestampId != self._lastTimestampId or not self._timestampSet:
                self._debug.log(f'Auto clear - timestamp changed, exiting thread #{initialTimestampId}')
                return

        self._debug.log(f'Auto clear - clearing timestamp #{initialTimestampId}')
        events.timestampCleared()
