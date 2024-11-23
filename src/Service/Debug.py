import src.events as events
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Configuration import Configuration
from src.Service.Logger import Logger


class Debug:
    _logger: Logger

    _debugEnabled: bool

    def __init__(self, config: Configuration, argumentParser: ArgumentParser, logger: Logger):
        self._logger = logger
        self._debugEnabled = config.get(config.DEBUG) or argumentParser.isDebugEnabled()

        if self._debugEnabled:
            events.clipboardChanged.append(lambda content: self._logger.log('Clipboard changed: ' + str(content)))
            events.timestampChanged.append(lambda timestamp: self._logger.log('Timestamp detected: ' + str(timestamp)))
            events.timestampClear.append(lambda: self._logger.log('Timestamp cleared'))

    def isDebugEnabled(self) -> bool:
        return self._debugEnabled
