from abc import ABC, abstractmethod

from src.Constant.AppConstant import AppConstant
from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Configuration import Configuration
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


# TODO rename: remove v2
class AutostartManagerV2(ABC):
    _filesystemHelper: FilesystemHelper
    _config: Configuration
    _argParser: ArgumentParser
    _logger: Logger

    _appNamePretty: str
    _appExecutablePath: str | None

    def __init__(
        self,
        filesystemHelper: FilesystemHelper,
        config: Configuration,
        argParser: ArgumentParser,
        logger: Logger,
    ):
        self._filesystemHelper = filesystemHelper
        self._config = config
        self._argParser = argParser
        self._logger = logger

        self._appNamePretty = AppConstant.appName
        self._appExecutablePath = filesystemHelper.getAppExecutablePath()

        if argParser.getMockPackaged():
            self._appExecutablePath = '/home/username/Apps/Statusbar Converter'

    def isAutostartSupported(self) -> bool:
        return self._filesystemHelper.isPackagedApp() or self._argParser.getMockPackaged()

    def setupAutostart(self) -> None:
        try:
            if not self.isAutostartSupported():
                self._logger.log(f'{Logs.catAutostart}Setup aborted: not a packaged app')

                return

            initialSetupCompleted = self._config.getState(ConfigId.Data_Autostart_InitialSetupComplete, False)
            enabled = self._config.getState(ConfigId.Data_Autostart_Enabled, False)

            self._logger.log(f'{Logs.catAutostart}Starting setup. enabled={enabled}, initialSetupCompleted={initialSetupCompleted}')

            if not initialSetupCompleted:
                if enabled:
                    self._logger.log(f'{Logs.catAutostart}Found invalid state. enabled=True, initialSetupCompleted=False. Setting initialSetupCompleted=True')
                    self._config.setState(ConfigId.Data_Autostart_InitialSetupComplete, True)
                else:
                    self._runInitialSetup()

                    return

            if not enabled:
                self._logger.log(f'{Logs.catAutostart}Autostart is disabled. Setup complete')

                return

            if not self._validateSetup():
                self._logger.log(f'{Logs.catAutostart}Expected and actual autostart setup don\'t match, will re-enable autostart')

                self.enableAutostart()
            else:
                self._logger.log(f'{Logs.catAutostart}Existing setup is valid')
        except Exception as e:
            self._logger.log(f'{Logs.catAutostart}EXCEPTION in AUTOSTART SETUP:\n{ExceptionHandler.formatExceptionLog(e)}')

    def _runInitialSetup(self) -> None:
        self._logger.log(f'{Logs.catAutostart}Starting initial setup')
        self.enableAutostart()
        self._config.setState(ConfigId.Data_Autostart_InitialSetupComplete, True)

    def enableAutostart(self) -> bool:
        """
        :return: Was autostart enabled successfully?
        """

        try:
            if not self.isAutostartSupported():
                self._logger.log(f'{Logs.catAutostart}Attempted autostart enable. Cannot complete because not in a packaged app')

                return False

            output = self._enableAutostartOsSpecific()

            self._config.setState(ConfigId.Data_Autostart_Enabled, True)
            self._logger.log(f'{Logs.catAutostart}Enabled autostart, output: {output}')

            return True
        except Exception as e:
            self._logger.log(f'{Logs.catAutostart}EXCEPTION in AUTOSTART ENABLE:\n{ExceptionHandler.formatExceptionLog(e)}')

            return False

    @abstractmethod
    def _enableAutostartOsSpecific(self) -> str | None:
        pass

    def disableAutostart(self) -> bool:
        try:
            if not self.isAutostartSupported():
                self._logger.log(f'{Logs.catAutostart}Attempted autostart disable. Cannot complete because not in a packaged app')

                return False

            output = self._disableAutostartOsSpecific()

            self._config.setState(ConfigId.Data_Autostart_Enabled, False)
            self._logger.log(f'{Logs.catAutostart}Disabled autostart, output: {output}')

            return True
        except Exception as e:
            self._logger.log(f'{Logs.catAutostart}EXCEPTION in AUTOSTART DISABLE:\n{ExceptionHandler.formatExceptionLog(e)}')

            return False

    @abstractmethod
    def _disableAutostartOsSpecific(self) -> str | None:
        pass

    @abstractmethod
    def _validateSetup(self) -> bool:
        pass

    def isAutostartEnabled(self) -> bool:
        return self._config.getState(ConfigId.Data_Autostart_Enabled, False)
