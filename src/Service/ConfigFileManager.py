import os
import shutil
from src.Service.FilesystemHelper import FilesystemHelper


class ConfigFileManager:
    CONFIG_APP_PATH: str
    CONFIG_USER_PATH: str
    CONFIG_USER_EXAMPLE_PATH: str
    STATE_DATA_PATH: str
    STATE_DATA_EXAMPLE_PATH: str

    def __init__(self, filesystemHelper: FilesystemHelper):
        self.CONFIG_APP_PATH = filesystemHelper.getConfigDir() + '/config.app.yml'
        self.CONFIG_USER_PATH = filesystemHelper.getUserDataDir() + '/config.user.yml'
        self.CONFIG_USER_EXAMPLE_PATH = filesystemHelper.getConfigDir() + '/config.user.example.yml'
        self.STATE_DATA_PATH = filesystemHelper.getUserDataDir() + '/app.data.yml'
        self.STATE_DATA_EXAMPLE_PATH = filesystemHelper.getConfigDir() + '/app.data.example.yml'

    def getAppConfigContent(self) -> str:
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Loading app config from `{self.CONFIG_APP_PATH}` ... ', end='')

        with open(self.CONFIG_APP_PATH, 'r') as appConfigFile:
            appConfigContent = appConfigFile.read()
            print('done')

            return appConfigContent

    def getUserConfigContent(self) -> str:
        return self._getUserFile('user config', self.CONFIG_USER_EXAMPLE_PATH, self.CONFIG_USER_PATH)

    def getStateDataContent(self) -> str:
        return self._getUserFile('state data', self.STATE_DATA_EXAMPLE_PATH, self.STATE_DATA_PATH)

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
