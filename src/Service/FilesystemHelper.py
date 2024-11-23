import os
from abc import ABCMeta, abstractmethod


class FilesystemHelper(metaclass=ABCMeta):
    def getInitializationLogs(self) -> str:
        # We cannot directly use Logger because of circular imports, so we only return info to log
        return (
            f'Project dir: `{FilesystemHelper.getProjectDir()}`\n'
            f'User data dir: `{self.getUserDataDir()}`\n'
        )

    @staticmethod
    def getAssetsDir() -> str:
        """Get Assets directory (inside project directory)"""
        return FilesystemHelper.getProjectDir() + '/assets'

    @staticmethod
    def getConfigDir() -> str:
        """Get default app config directory (inside project directory)"""
        return FilesystemHelper.getProjectDir() + '/config'

    @abstractmethod
    def getUserDataDir(self) -> str:
        """Get directory for user config, state, logs and other data"""
        pass

    @staticmethod
    def getBinariesDir() -> str:
        """Get directory for embedded binaries"""
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
        """Get directory where scripts should be saved to enable auto-start on boot"""
        pass
