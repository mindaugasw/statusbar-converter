import os
from src.Service.AutostartManager import AutostartManager
from src.Service.FilesystemHelperMacOs import FilesystemHelperMacOs


class AutostartManagerMacOS(AutostartManager):
    def enableAutostart(self) -> bool:
        appPath = FilesystemHelperMacOs.getAppPath()

        if appPath is None:
            self._debug.log('Autostart: can\'t enable autostart, code is not packaged into an app')

            return False

        if 'Applications' not in appPath:
            # Here we don't enable autostart if not in /Applications because user may
            # start the app for the first time from Downloads or some other location, and
            # possibly later move it to /Applications, which will invalidate login item
            self._debug.log('Autostart: can\'t enable autostart, app is not inside Applications directory')

            return False

        os.popen(f'login-items add {appPath}')
        self._debug.log('Autostart: added login item')

        return True

    def disableAutostart(self) -> None:
        os.popen(f'login-items rm "{self._appName}"')
        self._debug.log('Autostart: removed login item')

    def isEnabledAutostart(self) -> bool:
        loginItems = os.popen('login-items paths').read()
        loginItems = loginItems.splitlines()

        for loginItem in loginItems:
            if self._appName in loginItem:
                return True

        return False
