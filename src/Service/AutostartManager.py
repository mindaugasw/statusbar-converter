from abc import ABC, abstractmethod

from src.Constant.AppConstant import AppConstant
from src.Constant.ConfigId import ConfigId
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


# TODO remove
class AutostartManager(ABC):
    _configuration: Configuration
    _filesystemHelper: FilesystemHelper
    _logger: Logger

    _appName: str
    _appPath: str | None

    def __init__(self, configuration: Configuration, filesystemHelper: FilesystemHelper, logger: Logger):
        self._configuration = configuration
        self._filesystemHelper = filesystemHelper
        self._logger = logger

        self._appName = AppConstant.appName
        self._appPath = filesystemHelper.getAppExecutablePath()

    def firstTimeSetup(self) -> None:
        if self._configuration.getState(ConfigId.Data_Autostart_InitialSetupComplete, False):
            self._logger.log('[Autostart] Initial setup already completed')

            return

        if self.isEnabledAutostart():
            self._logger.log('[Autostart] Autostart already enabled, skipping initial setup')

            return

        self._logger.log('[Autostart] Starting initial setup')
        success = self.enableAutostart()

        if success:
            self._configuration.setState(ConfigId.Data_Autostart_InitialSetupComplete, True)

        self._logger.log(f'[Autostart] Initial setup completed, success: {success}')

    @abstractmethod
    def enableAutostart(self) -> bool:
        pass

    @abstractmethod
    def disableAutostart(self) -> None:
        pass

    @abstractmethod
    def isEnabledAutostart(self) -> bool:
        pass
