from src.Constant.ConfigId import ConfigId
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Configuration import Configuration


class Debug:
    _debugEnabled: bool
    _mockUpdate: str | None

    def __init__(self, config: Configuration, argumentParser: ArgumentParser):
        self._debugEnabled = config.get(ConfigId.Debug) or argumentParser.isDebugEnabled()
        self._mockUpdate = argumentParser.getMockUpdate()

        if self._mockUpdate is not None and self._mockUpdate != 'new' and self._mockUpdate != 'old':
            raise Exception(f'Invalid value provided for --mock-update: {self._mockUpdate}')

    def isDebugEnabled(self) -> bool:
        return self._debugEnabled

    def getMockUpdate(self) -> str | None:
        return self._mockUpdate
