import os
import shutil
from src.Service.FilesystemHelper import FilesystemHelper


class ConfigFileManager:
    configUserPath: str

    _configAppPath: str
    _configUserExamplePath: str

    def __init__(self, filesystemHelper: FilesystemHelper):
        self._configAppPath = filesystemHelper.getConfigDir() + '/config.app.yml'
        self._configUserExamplePath = filesystemHelper.getConfigDir() + '/config.user.example.yml'
        self.configUserPath = filesystemHelper.getUserDataDir() + '/config.user.yml'

    def getAppConfigContent(self) -> str:
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Loading app config from `{self._configAppPath}` ... ', end='')

        with open(self._configAppPath, 'r') as appConfigFile:
            appConfigContent = appConfigFile.read()
            print('done')

            return appConfigContent

    def getUserConfigContent(self) -> str:
        if not self._userConfigExists():
            self._createUserConfig()

        print(f'Loading user config from `{self.configUserPath}` ... ', end='')

        with open(self.configUserPath, 'r') as userConfigFile:
            userConfigContent = userConfigFile.read()
            print('done')

            return userConfigContent

    def _userConfigExists(self) -> bool:
        return os.path.isfile(self.configUserPath)

    def _createUserConfig(self) -> None:
        print(f'Creating user config at `{self.configUserPath}` from `{self._configUserExamplePath}` ... ', end='')
        shutil.copyfile(self._configUserExamplePath, self.configUserPath)
        print('done')
