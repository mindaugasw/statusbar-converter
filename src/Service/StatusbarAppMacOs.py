import os
import subprocess
import sys
import threading
import time
from rumps import App, MenuItem, rumps
import src.events as events
from src.Service.Debug import Debug
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampParser import TimestampParser
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.FilesystemHelper import FilesystemHelper
from src.Entity.Timestamp import Timestamp


class StatusbarAppMacOs(StatusbarApp):
    WEBSITE = 'https://github.com/mindaugasw/statusbar-converter'

    _clipboard: ClipboardManager
    _timestampParser: TimestampParser
    _configFileManager: ConfigFileManager
    _app: App

    _menuItems: dict[str, MenuItem | None]
    _menuTemplatesLastTimestamp: dict[str, str]
    _menuTemplatesCurrentTimestamp: dict[str, str]

    def __init__(
        self,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        timestampParser: TimestampParser,
        config: Configuration,
        configFileManager: ConfigFileManager,
        debug: Debug,
    ):
        super().__init__(formatter, config, debug)

        self._iconPathDefault = FilesystemHelper.getAssetsDir() + '/icon_macos.png'
        self._iconPathFlash = FilesystemHelper.getAssetsDir() + '/icon_macos_flash.png'

        self._clipboard = clipboard
        self._timestampParser = timestampParser
        self._configFileManager = configFileManager
        self._debug = debug

        self._menuTemplatesLastTimestamp = config.get(config.MENU_ITEMS_LAST_TIMESTAMP)
        self._menuTemplatesCurrentTimestamp = config.get(config.MENU_ITEMS_CURRENT_TIMESTAMP)

    def createApp(self) -> None:
        events.timestampChanged.append(self._onTimestampChange)
        events.timestampClear.append(self._onTimestampClear)

        self._menuItems = self._createMenuItems()
        self._app = App(
            StatusbarApp.APP_NAME,
            None,
            self._iconPathDefault,
            True,
            self._menuItems.values(),
        )
        self._app.run()

    def _createMenuItems(self) -> dict[str, MenuItem | None]:
        lastTimestamp = Timestamp()
        menu: dict[str, MenuItem | None] = {}

        if len(self._menuTemplatesLastTimestamp) != 0:
            menu.update({
                'last_timestamp_label': MenuItem('Last timestamp - click to copy'),
            })

            for key, template in self._menuTemplatesLastTimestamp.items():
                menu.update({key: MenuItem(
                    self._formatter.format(lastTimestamp, template),
                    self._onMenuClickLastTime,
                )})

            menu.update({'separator_last_timestamp': None})

        if len(self._menuTemplatesCurrentTimestamp) != 0:
            menu.update({
                'current_timestamp_label': MenuItem('Current timestamp - click to copy'),
            })

            for key, template in self._menuTemplatesCurrentTimestamp.items():
                menu.update({key: MenuItem(key, self._onMenuClickCurrentTime)})

            menu.update({'separator_current_timestamp': None})

        menu.update({
            'clear_timestamp': MenuItem('Clear timestamp', self._onMenuClickClearTimestamp),
            'edit_config': MenuItem('Edit configuration', self._onMenuClickEditConfiguration),
            'check_for_updates': MenuItem('Check for updates'),  # TODO implement check for updates
            'open_website': MenuItem('Open website', self._onMenuClickOpenWebsite),
            'restart': MenuItem('Restart application', self._onMenuClickRestart),
        })

        return menu

    def _onTimestampChange(self, timestamp: Timestamp) -> None:
        title = self._formatter.formatForIcon(timestamp)
        self._debug.log(f'Changing statusbar to: {title}')
        self._app.title = title

        for key, template in self._menuTemplatesLastTimestamp.items():
            self._menuItems[key].title = self._formatter.format(timestamp, template)

        if self._flashIconOnChange:
            threading.Thread(target=self._flashIcon).start()

    def _flashIcon(self) -> None:
        self._app.icon = self._iconPathFlash
        time.sleep(StatusbarAppMacOs.ICON_FLASH_DURATION)
        self._app.icon = self._iconPathDefault

    def _onTimestampClear(self) -> None:
        self._app.title = None

    def _onMenuClickLastTime(self, item: MenuItem) -> None:
        self._clipboard.setClipboardContent(item.title)

    def _onMenuClickCurrentTime(self, item: MenuItem) -> None:
        template = self._menuTemplatesCurrentTimestamp[item.title]
        text = self._formatter.format(Timestamp(), template)

        self._clipboard.setClipboardContent(text)

    def _onMenuClickClearTimestamp(self, item: MenuItem) -> None:
        events.timestampClear()

    def _onMenuClickEditConfiguration(self, item: MenuItem) -> None:
        configFilePath = self._configFileManager.configUserPath

        alertResult = rumps.alert(
            title='Edit configuration',
            message='Configuration can be edited in the file: \n'
            f'{configFilePath}\n\n'
            'After editing, the application must be restarted.\n\n'
            'All supported configuration can be found at:\n'
            'https://github.com/mindaugasw/timestamp-statusbar-converter/blob/master/config.app.yml',
            ok='Open in default editor',
            cancel='Close',
            icon_path=self._iconPathFlash,
        )

        if alertResult == 1:
            subprocess.Popen(['open', configFilePath])

    def _onMenuClickOpenWebsite(self, item: MenuItem) -> None:
        subprocess.Popen(['open', StatusbarAppMacOs.WEBSITE])
        # TODO use xdg-open on Linux
        # https://stackoverflow.com/a/4217323/4110469

    def _onMenuClickRestart(self, item: MenuItem) -> None:
        os.execl(sys.executable, '-m src.main', *sys.argv)
