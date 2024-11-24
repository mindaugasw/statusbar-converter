import os.path
import pathlib

from src.Service.AutostartManager import AutostartManager
from src.Service.FilesystemHelperLinux import FilesystemHelperLinux


class AutostartManagerLinux(AutostartManager):
    _autostartScriptPath: str

    def firstTimeSetup(self) -> None:
        self._autostartScriptPath = f'{FilesystemHelperLinux.getStartupScriptDir()}/{self._appName}.desktop'

        if self._appPath is None or '/Downloads/' in self._appPath:
            # Here we don't enable autostart automatically if app is in Downloads
            # directory, since user may soon move the app somewhere else and autostart
            # config will remain broken
            self._logger.log('[Autostart] Not a packaged app or is inside Downloads directory, skipping initial setup')

            return

        super().firstTimeSetup()

    def enableAutostart(self) -> bool:
        if self._appPath is None:
            self._logger.log('[Autostart] can\'t enable autostart, code is not packaged into an app')

            return False

        exampleScriptPath = f'{self._filesystemHelper.getConfigDir()}/linux-startup.desktop'

        with open(exampleScriptPath, 'r') as exampleScriptFile:
            scriptContent = exampleScriptFile.read()

        scriptContent = scriptContent.format(path=f'"{self._appPath}"', name=self._appName)

        with open(self._autostartScriptPath, 'w') as scriptFile:
            scriptFile.write(scriptContent)

        self._logger.log('[Autostart] Added login item')

        return True

    def disableAutostart(self) -> None:
        pathlib.Path.unlink(pathlib.Path(self._autostartScriptPath), missing_ok=True)
        self._logger.log('[Autostart] Removed login item')

    def isEnabledAutostart(self) -> bool:
        if self._appPath is None:
            return False

        # Ideally this should parse the file and check if Exec path matches current path.
        # So that it would return False if app was moved and script is no longer valid.
        # However, CLI arguments make path check much more complicated.
        # A task for the future
        return os.path.isfile(self._autostartScriptPath)
