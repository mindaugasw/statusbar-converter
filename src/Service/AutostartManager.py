from abc import ABCMeta, abstractmethod

from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class AutostartManager(metaclass=ABCMeta):
    _configuration: Configuration
    _filesystemHelper: FilesystemHelper
    _logger: Logger

    _appName: str
    _appPath: str | None

    def __init__(self, configuration: Configuration, filesystemHelper: FilesystemHelper, logger: Logger):
        self._configuration = configuration
        self._filesystemHelper = filesystemHelper
        self._logger = logger

        self._appPath = filesystemHelper.getAppPath()

    def firstTimeSetup(self) -> None:
        if self._configuration.getState(Configuration.DATA_AUTO_RUN_INITIAL_SETUP_COMPLETE):
            self._logger.log('Autostart: initial setup already completed')

            return

        if self.isEnabledAutostart():
            self._logger.log('Autostart: autostart already enabled, skipping initial setup')

            return

        self._logger.log('Autostart: starting initial setup')
        success = self.enableAutostart()

        if success:
            self._configuration.setState(Configuration.DATA_AUTO_RUN_INITIAL_SETUP_COMPLETE, True)

        self._logger.log(f'Autostart: initial setup completed, success: {success}')

    @abstractmethod
    def enableAutostart(self) -> bool:
        pass

    @abstractmethod
    def disableAutostart(self) -> None:
        pass

    @abstractmethod
    def isEnabledAutostart(self) -> bool:
        pass

    def setAppName(self, appName) -> None:
        # Separate setter needed (instead of accessing directly from StatusbarApp class) to avoid circular import error
        self._appName = appName
