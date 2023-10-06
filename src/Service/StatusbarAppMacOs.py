import os
import subprocess
import threading
import time
import rumps
import src.events as events
from src.Entity.MenuItem import MenuItem
from src.Service.Debug import Debug
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.UpdateManager import UpdateManager
from src.Entity.Timestamp import Timestamp


class StatusbarAppMacOs(StatusbarApp):
    _app: rumps.App

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        config: Configuration,
        configFileManager: ConfigFileManager,
        updateManager: UpdateManager,
        debug: Debug,
    ):
        super().__init__(osSwitch, formatter, clipboard, config, configFileManager, updateManager, debug)

        self._iconPathDefault = FilesystemHelper.getAssetsDir() + '/icon_macos.png'
        self._iconPathFlash = FilesystemHelper.getAssetsDir() + '/icon_macos_flash.png'

    def createApp(self) -> None:
        events.timestampChanged.append(self._onTimestampChange)
        events.timestampClear.append(self._onTimestampClear)

        menu = self._createOsNativeMenu(self._createCommonMenu())

        self._app = rumps.App(
            StatusbarApp.APP_NAME,
            None,
            self._iconPathDefault,
            True,
            menu.values(),
        )

        self._app.run()

    def _createOsNativeMenu(self, commonMenu: dict[str, MenuItem]) -> dict[str, rumps.MenuItem | None]:
        menu: dict[str, MenuItem | None] = {}

        item: MenuItem
        for key, item in commonMenu.items():
            if item.isSeparator:
                menu.update({key: None})

                continue

            nativeItem = rumps.MenuItem(
                item.label,
                None if item.isDisabled else item.callback,
            )

            item.setNativeItem(nativeItem)
            menu.update({key: nativeItem})

        return menu

    def _showAppUpdateDialog(self, version: str | None) -> None:
        # Here dialog cannot be shown by rumps because it's called from a different thread.
        # Can't be called from the main thread because of async request.
        # Also, automatic update check can't trigger dialog from rumps main thread

        buttons = {
            'download': 'Download update',
            'skip': 'Skip this version',
            'later': 'Remind me later',
        }

        if version is None:
            dialogCommand =\
                f'osascript -e \'Tell application "System Events" to display dialog ' \
                f'"No new version found.\\n' \
                f'Current app version is v{self._config.getAppVersion()}." ' \
                f'with title "{StatusbarAppMacOs.APP_NAME}" ' \
                f'buttons {{"Ok"}} ' \
                f'default button "Ok" ' \
                f'with icon POSIX file "{self._iconPathDefault}"\''
        else:
            dialogCommand =\
                f'osascript -e \'Tell application "System Events" to display dialog ' \
                f'"New app update found: {version}.\\n' \
                f'Current app version is v{self._config.getAppVersion()}.\\n' \
                f'Release notes available on the download page.\\n\\n' \
                f'Download update?" ' \
                f'with title "{StatusbarAppMacOs.APP_NAME}" ' \
                f'buttons {{"{buttons["download"]}", "{buttons["skip"]}", "{buttons["later"]}"}} ' \
                f'default button "Download update" ' \
                f'with icon POSIX file "{self._iconPathDefault}"\''

        result = os.popen(dialogCommand).read()
        result = result.strip().replace('button returned:', '')
        self._debug.log(f'Update check: user action: {result}')

        if version is None:
            return

        if result == buttons['download']:
            subprocess.Popen(['open', f'{StatusbarAppMacOs.WEBSITE}/releases/tag/{version}'])
        elif result == buttons['skip']:
            self._config.setState(Configuration.DATA_UPDATE_SKIP_VERSION, version)
        elif result == buttons['later']:
            return
        else:
            self._debug.log(f'Update check: unknown user action: {result}')

    def _onMenuClickLastTimestamp(self, menuItem: rumps.MenuItem) -> None:
        self._clipboard.setClipboardContent(menuItem.title)

    def _onMenuClickCurrentTimestamp(self, menuItem: rumps.MenuItem) -> None:
        template = self._menuTemplatesCurrentTimestamp[menuItem.title]
        text = self._formatter.format(Timestamp(), template)

        self._clipboard.setClipboardContent(text)

    def _onMenuClickEditConfiguration(self, menuItem: rumps.MenuItem) -> None:
        # TODO replace with applescript
        alertResult = rumps.alert(
            title='Edit configuration',
            message='Configuration can be edited in the file: \n'
            f'{self._configFilePath}\n\n'
            'After editing, the application must be restarted.\n\n'
            'All supported configuration can be found at:\n'
            f'{StatusbarAppMacOs.WEBSITE}/blob/master/config.app.yml',
            ok='Open in default editor',
            cancel='Close',
            icon_path=self._iconPathDefault,
        )

        if alertResult == 1:
            subprocess.Popen(['open', self._configFilePath])

    def _onMenuClickOpenWebsite(self, menuItem: rumps.MenuItem) -> None:
        subprocess.Popen(['open', StatusbarAppMacOs.WEBSITE])

    def _onMenuClickAbout(self, menuItem: rumps.MenuItem) -> None:
        # TODO replace with applescript
        rumps.alert(
            title=StatusbarAppMacOs.APP_NAME,
            message='Version: ' + self._config.getAppVersion() + '\n\nApp icon made by iconsax at flaticon.com',
            icon_path=self._iconPathDefault,
        )

    def _onTimestampChange(self, timestamp: Timestamp) -> None:
        if self._flashIconOnChange:
            threading.Thread(target=self._flashIcon, daemon=True).start()

        title = self._formatter.formatForIcon(timestamp)
        self._debug.log(f'Changing statusbar to: {title}')
        self._app.title = title

        for key, template in self._menuTemplatesLastTimestamp.items():
            self._menuItems[key].nativeItem.title = self._formatter.format(timestamp, template)

    def _flashIcon(self) -> None:
        self._app.icon = self._iconPathFlash
        time.sleep(StatusbarAppMacOs.ICON_FLASH_DURATION)
        self._app.icon = self._iconPathDefault

    def _onTimestampClear(self) -> None:
        self._app.title = None
