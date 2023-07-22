import os
import shutil
from src.Service.FilesystemHelper import FilesystemHelper


class ConfigFileManager:
    CONFIG_APP_PATH: str
    CONFIG_USER_PATH: str
    CONFIG_USER_EXAMPLE_PATH: str

    def __init__(self, filesystemHelper: FilesystemHelper):
        self.CONFIG_APP_PATH = filesystemHelper.getConfigDir() + '/config.app.yml'
        self.CONFIG_USER_EXAMPLE_PATH = filesystemHelper.getConfigDir() + '/config.user.example.yml'
        self.CONFIG_USER_PATH = filesystemHelper.getUserDataDir() + '/config.user.yml'

    def getAppConfigContent(self) -> str:
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Loading app config from `{self.CONFIG_APP_PATH}` ... ', end='')

        with open(self.CONFIG_APP_PATH, 'r') as appConfigFile:
            appConfigContent = appConfigFile.read()
            print('done')

            return appConfigContent

    def getUserConfigContent(self) -> str:
        if not self._userConfigExists():
            self._createUserConfig()

        print(f'Loading user config from `{self.CONFIG_USER_PATH}` ... ', end='')

        with open(self.CONFIG_USER_PATH, 'r') as userConfigFile:
            userConfigContent = userConfigFile.read()
            print('done')

            return userConfigContent

    def _userConfigExists(self) -> bool:
        return os.path.isfile(self.CONFIG_USER_PATH)

    def _createUserConfig(self) -> None:
        print(f'Creating user config at `{self.CONFIG_USER_PATH}` from `{self.CONFIG_USER_EXAMPLE_PATH}` ... ', end='')
        shutil.copyfile(self.CONFIG_USER_EXAMPLE_PATH, self.CONFIG_USER_PATH)
        print('done')
