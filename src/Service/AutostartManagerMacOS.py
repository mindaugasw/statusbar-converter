import os
from src.Service.AutostartManager import AutostartManager


class AutostartManagerMacOS(AutostartManager):
    def firstTimeSetup(self) -> None:
        if self._appPath is None or 'Applications' not in self._appPath:
            # Here we don't enable autostart automatically if not in /Applications because
            # user may start the app for the first time from Downloads or some other location,
            # and possibly later move it to /Applications, which will invalidate login item
            self._debug.log('Autostart: app is not inside Applications directory, skipping initial setup')

            return

        super().firstTimeSetup()

    def enableAutostart(self) -> bool:
        if self._appPath is None:
            self._debug.log('Autostart: can\'t enable autostart, code is not packaged into an app')

            return False

        command = 'osascript -e \'tell application "System Events" to make login item at end ' \
                  f'with properties {{path:"{self._appPath}", hidden:false}}\''
        os.popen(command)
        self._debug.log('Autostart: added login item')

        return True

    def disableAutostart(self) -> None:
        os.popen(f'osascript -e \'tell application "System Events" to delete login item "{self._appName}"\'')
        self._debug.log('Autostart: removed login item')

    def isEnabledAutostart(self) -> bool:
        command = 'osascript -e \'tell application "System Events" to get the path of every login item\''
        loginItems = os.popen(command).read().split(', ')

        for loginItem in loginItems:
            if self._appName in loginItem:
                return True

        return False
