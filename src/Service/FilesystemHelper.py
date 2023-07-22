import os
import rumps
from src.Service.StatusbarApp import StatusbarApp


class FilesystemHelper:
    def __init__(self):
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Project dir: `{self._getProjectDir()}`')
        print(f'User data dir: `{self.getUserDataDir()}`')

    def getAssetsDir(self) -> str:
        return self._getProjectDir() + '/assets'

    def getConfigDir(self) -> str:
        return self._getProjectDir() + '/config'

    def getUserDataDir(self) -> str:
        return rumps.application_support(StatusbarApp.APP_NAME)

    def _getProjectDir(self) -> str:
        return os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
