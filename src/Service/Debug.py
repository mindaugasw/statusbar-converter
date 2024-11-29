from src.Service.ArgumentParser import ArgumentParser
from src.Service.Configuration import Configuration


class Debug:
    _debugEnabled: bool

    def __init__(self, config: Configuration, argumentParser: ArgumentParser):
        self._debugEnabled = config.get(config.DEBUG) or argumentParser.isDebugEnabled()

    def isDebugEnabled(self) -> bool:
        return self._debugEnabled
