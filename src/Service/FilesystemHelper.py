import os
import sys
from abc import ABC, abstractmethod


class FilesystemHelper(ABC):
    def getInitializationLogs(self) -> str:
        # We cannot directly use Logger because of circular imports, so we only return info to log
        return (
            f'Project dir: `{self.getProjectDir()}`\n'
            f'User data dir: `{self.getUserDataDir()}`\n'
        )

    def getAssetsDir(self) -> str:
        """Get Assets directory (inside project directory)"""
        return self.getProjectDir() + '/assets'

    def getAssetsDevDir(self) -> str:
        """
        Get Assets directory (inside project directory) for development-only files

        Split into a separate directory from other assets to allow excluding it from build
        """
        return self.getProjectDir() + '/assets_dev'

    def getConfigDir(self) -> str:
        """Get default app config directory (inside project directory)"""
        return self.getProjectDir() + '/config'

    @abstractmethod
    def getUserDataDir(self) -> str:
        """Get directory for user config, state, logs and other data"""
        pass

    def getBinariesDir(self) -> str:
        """Get directory for embedded binaries"""
        return self.getProjectDir() + '/binaries'

    def getProjectDir(self) -> str:
        return os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')

    @abstractmethod
    def getAppExecutablePath(self) -> str | None:
        """Get path to the application file.

        Will return path to the app or None if code is not packaged into an app.
        App path on macOS is .app archive. App path on Linux it is app file.
        """
        pass

    @abstractmethod
    def getStartupScriptDir(self) -> str:
        """Get directory where scripts should be saved to enable auto-start on boot"""
        pass

    def isPackagedApp(self):
        # Frozen attribute is added by PyInstaller to packaged app
        return getattr(sys, 'frozen', False)

    @abstractmethod
    def openFile(self, filePath: str) -> None:
        """Open file in system-default application"""
        pass
