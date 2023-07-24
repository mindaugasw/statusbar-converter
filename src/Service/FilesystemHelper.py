import os
from abc import ABCMeta, abstractmethod


class FilesystemHelper(metaclass=ABCMeta):
    def __init__(self):
        # Debug service is not yet initialized, so we simply always print debug information
        print(f'Project dir: `{FilesystemHelper._getProjectDir()}`')
        print(f'User data dir: `{self.getUserDataDir()}`')

    @staticmethod
    def getAssetsDir() -> str:
        return FilesystemHelper._getProjectDir() + '/assets'

    @staticmethod
    def getConfigDir() -> str:
        return FilesystemHelper._getProjectDir() + '/config'

    @abstractmethod
    def getUserDataDir(self) -> str:
        pass

    @staticmethod
    def getBinariesDir() -> str:
        return FilesystemHelper._getProjectDir() + '/binaries'

    @staticmethod
    def _getProjectDir() -> str:
        return os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
