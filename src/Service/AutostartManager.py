from abc import ABCMeta, abstractmethod
from src.Service.Debug import Debug
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper


class AutostartManager(metaclass=ABCMeta):
    _configuration: Configuration
    _filesystemHelper: FilesystemHelper
    _debug: Debug

    _appName: str
    _appPath: str | None

    def __init__(self, configuration: Configuration, filesystemHelper: FilesystemHelper, debug: Debug):
        self._configuration = configuration
        self._filesystemHelper = filesystemHelper
        self._debug = debug

        self._appPath = filesystemHelper.getAppPath()

    def firstTimeSetup(self) -> None:
        if self._configuration.getState(Configuration.DATA_AUTO_RUN_INITIAL_SETUP_COMPLETE):
            self._debug.log('Autostart: initial setup already completed')

            return

        if self.isEnabledAutostart():
            self._debug.log('Autostart: autostart already enabled, skipping initial setup')

            return

        self._debug.log('Autostart: starting initial setup')
        success = self.enableAutostart()

        if success:
            self._configuration.setState(Configuration.DATA_AUTO_RUN_INITIAL_SETUP_COMPLETE, True)

        self._debug.log(f'Autostart: initial setup completed, success: {success}')

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
