import os
import shutil
import rumps
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp


class ConfigFileManager:
    CONFIG_APP_PATH: str
    CONFIG_USER_PATH: str
    CONFIG_USER_EXAMPLE_PATH: str

    def __init__(self, filesystemHelper: FilesystemHelper):
        self.CONFIG_APP_PATH = filesystemHelper.getProjectDir() + '/config/config.app.yml'
        self.CONFIG_USER_EXAMPLE_PATH = filesystemHelper.getProjectDir() + '/config/config.user.example.yml'
        self.CONFIG_USER_PATH = rumps.application_support(StatusbarApp.APP_NAME) + '/config.user.yml'

    def getAppConfigContent(self) -> str:
        with open(self.CONFIG_APP_PATH, 'r') as appConfigFile:
            return appConfigFile.read()

    def getUserConfigContent(self) -> str:
        if not self._userConfigExists():
            self._createUserConfig()

        with open(self.CONFIG_USER_PATH, 'r') as userConfigFile:
            return userConfigFile.read()

    def _userConfigExists(self) -> bool:
        return os.path.isfile(self.CONFIG_USER_PATH)

    def _createUserConfig(self) -> None:
        shutil.copyfile(self.CONFIG_USER_EXAMPLE_PATH, self.CONFIG_USER_PATH)
