import os
import sys
from abc import ABCMeta, abstractmethod
import src.events as events
from src.Entity.MenuItem import MenuItem
from src.Entity.Timestamp import Timestamp
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.OSSwitch import OSSwitch
from src.Service.TimestampTextFormatter import TimestampTextFormatter


class StatusbarApp(metaclass=ABCMeta):
    APP_NAME = 'Statusbar Converter'
    WEBSITE = 'https://github.com/mindaugasw/statusbar-converter'
    ICON_FLASH_DURATION = 0.35

    appVersion: str

    _osSwitch: OSSwitch
    _formatter: TimestampTextFormatter
    _clipboard: ClipboardManager
    _debug: Debug

    _menuItems: dict[str, MenuItem]
    _menuTemplatesLastTimestamp: dict[str, str]
    _menuTemplatesCurrentTimestamp: dict[str, str]
    _iconPathDefault: str
    _iconPathFlash: str
    _flashIconOnChange: bool
    _configFilePath: str

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        config: Configuration,
        configFileManager: ConfigFileManager,
        debug: Debug,
    ):
        self._osSwitch = osSwitch
        self._formatter = formatter
        self._clipboard = clipboard
        self._debug = debug

        self._configFilePath = configFileManager.configUserPath

        self._menuTemplatesLastTimestamp = config.get(config.MENU_ITEMS_LAST_TIMESTAMP)
        self._menuTemplatesCurrentTimestamp = config.get(config.MENU_ITEMS_CURRENT_TIMESTAMP)
        self._flashIconOnChange = config.get(config.FLASH_ICON_ON_CHANGE)

        with open(FilesystemHelper.getProjectDir() + '/version', 'r') as versionFile:
            self.appVersion = versionFile.read().strip()

    @abstractmethod
    def createApp(self) -> None:
        pass

    def _createCommonMenu(self) -> dict[str, MenuItem]:
        lastTimestamp = Timestamp()
        items = {}

        if len(self._menuTemplatesLastTimestamp) != 0:
            items.update({'last_timestamp_label': MenuItem('Last timestamp - click to copy', True)})

            for key, template in self._menuTemplatesLastTimestamp.items():
                items.update({
                    key: MenuItem(
                        self._formatter.format(lastTimestamp, template),
                        callback=self._onMenuClickLastTimestamp,
                    )
                })

            items.update({'separator_last_timestamp': MenuItem(isSeparator=True)})

        if len(self._menuTemplatesCurrentTimestamp) != 0:
            items.update({'current_timestamp_label': MenuItem('Current timestamp - click to copy', True)})

            for key, template in self._menuTemplatesCurrentTimestamp.items():
                items.update({
                    key: MenuItem(key, callback=self._onMenuClickCurrentTimestamp)
                })

            items.update({'separator_current_timestamp': MenuItem(isSeparator=True)})

        items.update({
            'clear_timestamp': MenuItem('Clear timestamp', callback=self._onMenuClickClearTimestamp),
            'edit_config': MenuItem('Edit configuration', callback=self._onMenuClickEditConfiguration),
            'open_website': MenuItem('Open website', callback=self._onMenuClickOpenWebsite),
            'about': MenuItem('About', callback=self._onMenuClickAbout)
        })

        if self._osSwitch.isMacOS():
            # On Linux restart button throws error on 2nd restart, so we add the button only for macOS
            items.update({
                'restart': MenuItem('Restart application', callback=self._onMenuClickRestart),
            })

        if self._osSwitch.isLinux():
            # On macOS Quit button is automatically created by rumps app
            items.update({
                'quit': MenuItem('Quit', callback=self._onMenuClickQuit),
            })

        self._menuItems = items

        return items

    @abstractmethod
    def _createOsNativeMenu(self, commonMenu: dict[str, MenuItem]):
        pass

    @abstractmethod
    def _onMenuClickLastTimestamp(self, menuItem) -> None:
        pass

    @abstractmethod
    def _onMenuClickCurrentTimestamp(self, menuItem) -> None:
        pass

    def _onMenuClickClearTimestamp(self, menuItem) -> None:
        events.timestampClear()

    @abstractmethod
    def _onMenuClickEditConfiguration(self, menuItem) -> None:
        pass

    @abstractmethod
    def _onMenuClickOpenWebsite(self, menuItem) -> None:
        pass

    @abstractmethod
    def _onMenuClickAbout(self, menuItem) -> None:
        pass

    def _onMenuClickRestart(self, menuItem) -> None:
        # On Linux this fails on 2nd restart, sys.executable is not set after the 1st restart
        os.execl(sys.executable, '-m src.main', *sys.argv)

    def _onMenuClickQuit(self, menuItem) -> None:
        raise Exception('Not implemented')
