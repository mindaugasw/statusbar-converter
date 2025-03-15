import os
import shutil

from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class ConfigFileManager:
    configUserPath: str

    _logger: Logger

    _configAppPath: str
    _configUserExamplePath: str
    _stateDataPath: str
    _stateDataExamplePath: str

    def __init__(self, filesystemHelper: FilesystemHelper, logger: Logger):
        self._logger = logger

        self._configAppPath = filesystemHelper.getConfigDir() + '/config.app.yml'
        self._configUserExamplePath = filesystemHelper.getConfigDir() + '/config.user.example.yml'
        self.configUserPath = filesystemHelper.getUserDataDir() + '/config.user.yml'
        self._stateDataPath = filesystemHelper.getUserDataDir() + '/state.app.yml'
        self._stateDataExamplePath = filesystemHelper.getConfigDir() + '/state.app.example.yml'

    def getAppConfigContent(self) -> str:
        # Debug service is not yet initialized, so we always print debug information
        self._logger.logRaw(f'Loading app config from `{self._configAppPath}` ... ')

        with open(self._configAppPath, 'r') as appConfigFile:
            appConfigContent = appConfigFile.read()
            self._logger.logRaw('done\n')

            return appConfigContent

    def getUserConfigContent(self) -> str:
        return self._getUserFile('user config', self._configUserExamplePath, self.configUserPath)

    def getStateDataContent(self) -> str:
        return self._getUserFile('state data', self._stateDataExamplePath, self._stateDataPath)

    def writeStateData(self, content: str) -> None:
        with open(self._stateDataPath, 'w') as stateFile:
            stateFile.write(content)

    def _getUserFile(self, prettyName: str, exampleFilePath: str, targetFilePath: str) -> str:
        if not self._userFileExists(targetFilePath):
            self._createUserFile(prettyName, exampleFilePath, targetFilePath)

        self._logger.logRaw(f'Loading {prettyName} from `{targetFilePath}` ... ')

        with open(targetFilePath, 'r') as userFile:
            userFileContent = userFile.read()
            self._logger.logRaw('done\n')

            return userFileContent

    def _userFileExists(self, path: str) -> bool:
        return os.path.isfile(path)

    def _createUserFile(self, prettyName: str, exampleFilePath: str, targetFilePath: str) -> None:
        self._logger.logRaw(f'Creating {prettyName} at `{targetFilePath}` from `{exampleFilePath}` ... ')
        shutil.copyfile(exampleFilePath, targetFilePath)
        self._logger.logRaw('done\n')
