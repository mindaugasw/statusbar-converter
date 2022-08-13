import os
from abc import ABCMeta
import rumps
from src.Helper.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp


# TODO remove abstract class in case separate class won't be needed in linux
class ConfigFileManager(metaclass=ABCMeta):
    CONFIG_APP_PATH: str
    CONFIG_USER_PATH: str
    CONFIG_USER_EXAMPLE_PATH: str

    def __init__(self):
        self.CONFIG_APP_PATH = FilesystemHelper.getProjectDir() + '/config.app.yml'
        self.CONFIG_USER_EXAMPLE_PATH = FilesystemHelper.getProjectDir() + '/config.user.example.yml'
        self.CONFIG_USER_PATH = rumps.application_support(StatusbarApp.APP_NAME) + '/config.yml'

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
        os.popen(f'cp "{self.CONFIG_USER_EXAMPLE_PATH}" "{self.CONFIG_USER_PATH}"')
