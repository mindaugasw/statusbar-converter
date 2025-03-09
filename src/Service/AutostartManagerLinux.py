import pathlib

from src.Constant.Logs import Logs
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.Configuration import Configuration
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class AutostartManagerLinux(AutostartManager):
    _autostartScriptPath: str

    def __init__(
        self,
        filesystemHelper: FilesystemHelper,
        config: Configuration,
        argParser: ArgumentParser,
        logger: Logger,
    ):
        super().__init__(filesystemHelper, config, argParser, logger)

        self._autostartScriptPath = f'{filesystemHelper.getStartupScriptDir()}/{self._appNamePretty}.desktop'

    def _enableAutostartOsSpecific(self) -> str | None:
        scriptContent = self._getAutostartScriptTargetContent()

        with open(self._autostartScriptPath, 'w') as scriptFile:
            scriptFile.write(scriptContent)

        return None

    def _disableAutostartOsSpecific(self) -> str | None:
        pathlib.Path.unlink(pathlib.Path(self._autostartScriptPath), missing_ok=True)

        return None

    def _validateSetup(self) -> bool:
        targetContent = self._getAutostartScriptTargetContent()

        try:
            with open(self._autostartScriptPath, 'r') as scriptFile:
                actualContent = scriptFile.read()
        except Exception as e:
            self._logger.log(f'{Logs.catAutostart}Got EXCEPTION trying to read current autostart file:\n{ExceptionHandler.formatExceptionLog(e)}')
            actualContent = ''

        return targetContent == actualContent

    def _getAutostartScriptTargetContent(self) -> str:
        exampleScriptPath = f'{self._filesystemHelper.getConfigDir()}/linux-startup.desktop'

        with open(exampleScriptPath, 'r') as exampleScriptFile:
            scriptContent = exampleScriptFile.read()

        scriptContent = scriptContent.format(path=f'"{self._appExecutablePath}"', name=self._appNamePretty)

        return scriptContent
