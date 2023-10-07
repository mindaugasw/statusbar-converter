import os
import shutil
from src.Service.FilesystemHelper import FilesystemHelper


class ConfigFileManager:
    configUserPath: str

    _configAppPath: str
    _configUserExamplePath: str
    _stateDataPath: str
    _stateDataExamplePath: str

    def __init__(self, filesystemHelper: FilesystemHelper):
        self._configAppPath = filesystemHelper.getConfigDir() + '/config.app.yml'
        self._configUserExamplePath = filesystemHelper.getConfigDir() + '/config.user.example.yml'
        self.configUserPath = filesystemHelper.getUserDataDir() + '/config.user.yml'
        self._stateDataPath = filesystemHelper.getUserDataDir() + '/app.data.yml'
        self._stateDataExamplePath = filesystemHelper.getConfigDir() + '/app.data.example.yml'

    def getAppConfigContent(self) -> str:
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Loading app config from `{self._configAppPath}` ... ', end='')

        with open(self._configAppPath, 'r') as appConfigFile:
            appConfigContent = appConfigFile.read()
            print('done')

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

        print(f'Loading {prettyName} from `{targetFilePath}` ... ', end='')

        with open(targetFilePath, 'r') as userFile:
            userFileContent = userFile.read()
            print('done')

            return userFileContent

    def _userFileExists(self, path: str) -> bool:
        return os.path.isfile(path)

    def _createUserFile(self, prettyName: str, exampleFilePath: str, targetFilePath: str) -> None:
        print(f'Creating {prettyName} at `{targetFilePath}` from `{exampleFilePath}` ... ', end='')
        shutil.copyfile(exampleFilePath, targetFilePath)
        print('done')
