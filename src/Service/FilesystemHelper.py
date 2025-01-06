import os
import sys
from abc import ABC, abstractmethod


class FilesystemHelper(ABC):
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
    def getAssetsDevDir() -> str:
        """
        Get Assets directory (inside project directory) for development-only files

        Split into a separate directory from other assets to allow excluding it from build
        """
        return FilesystemHelper.getProjectDir() + '/assets_dev'

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
    def getAppExecutablePath() -> str | None:
        """Get path to the application file.

        Will return path to the app or None if code is not packaged into an app.
        App path on macOS is .app archive. App path on Linux it is app file.
        """
        pass

    @staticmethod
    @abstractmethod
    def getStartupScriptDir() -> str:
        """Get directory where scripts should be saved to enable auto-start on boot"""
        pass

    @staticmethod
    def isPackagedApp():
        # Frozen attribute is added by PyInstaller to packaged app
        return getattr(sys, 'frozen', False)
