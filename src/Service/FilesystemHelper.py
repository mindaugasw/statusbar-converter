import os
from abc import ABCMeta, abstractmethod


class FilesystemHelper(metaclass=ABCMeta):
    def __init__(self):
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Project dir: `{FilesystemHelper.getProjectDir()}`')
        print(f'User data dir: `{self.getUserDataDir()}`')

    @staticmethod
    def getAssetsDir() -> str:
        return FilesystemHelper.getProjectDir() + '/assets'

    @staticmethod
    def getConfigDir() -> str:
        return FilesystemHelper.getProjectDir() + '/config'

    @abstractmethod
    def getUserDataDir(self) -> str:
        pass

    @staticmethod
    def getBinariesDir() -> str:
        return FilesystemHelper.getProjectDir() + '/binaries'

    @staticmethod
    def getProjectDir() -> str:
        return os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')

    @staticmethod
    @abstractmethod
    def getAppPath() -> str | None:
        """Get path to the application file.

        On macOS will return path to .app or None if code is not packaged into an app
        """
        pass

    @staticmethod
    @abstractmethod
    def getStartupScriptDir() -> str:
        pass
