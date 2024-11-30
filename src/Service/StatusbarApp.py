import os
import sys
from abc import ABC, abstractmethod

import src.events as events
from src.Constant.ModalId import ModalId
from src.DTO.MenuItem import MenuItem
from src.DTO.Timestamp import Timestamp
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.ConversionManager import ConversionManager
from src.Service.Debug import Debug
from src.Service.Logger import Logger
from src.Service.ModalWindow import ModalWindowManager
from src.Service.OSSwitch import OSSwitch
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.UpdateManager import UpdateManager


class StatusbarApp(ABC):
    WEBSITE = 'https://github.com/mindaugasw/statusbar-converter'
    ICON_FLASH_DURATION = 0.35

    _osSwitch: OSSwitch
    _formatter: TimestampTextFormatter
    _clipboard: ClipboardManager
    _conversionManager: ConversionManager
    _config: Configuration
    _autostartManager: AutostartManager
    _updateManager: UpdateManager
    _modalWindowManager: ModalWindowManager
    _logger: Logger
    _debug: Debug

    _menuItems: dict[str, MenuItem]
    _menuTemplateLastConversionOriginalText: str
    _menuTemplateLastConversionConvertedText: str
    _menuTemplatesCurrentTimestamp: dict[str, str]
    _iconPathDefault: str
    _iconPathFlash: str
    _flashIconOnChange: bool
    _configFilePath: str

    _menuIdLastConversionOriginalText = 'last_conversion_original_text'
    _menuIdLastConversionConvertedText = 'last_conversion_converted_text'

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        conversionManager: ConversionManager,
        config: Configuration,
        configFileManager: ConfigFileManager,
        autostartManager: AutostartManager,
        updateManager: UpdateManager,
        modalWindowManager: ModalWindowManager,
        logger: Logger,
        debug: Debug,
    ):
        self._osSwitch = osSwitch
        self._formatter = formatter
        self._clipboard = clipboard
        self._conversionManager = conversionManager
        self._config = config
        self._autostartManager = autostartManager
        self._updateManager = updateManager
        self._modalWindowManager = modalWindowManager
        self._logger = logger
        self._debug = debug

        self._configFilePath = configFileManager.configUserPath

        self._menuTemplateLastConversionOriginalText = config.get(config.MENU_ITEMS_LAST_CONVERSION_ORIGINAL_TEXT)
        self._menuTemplateLastConversionConvertedText = config.get(config.MENU_ITEMS_LAST_CONVERSION_CONVERTED_TEXT)
        self._menuTemplatesCurrentTimestamp = config.get(config.MENU_ITEMS_CURRENT_TIMESTAMP)
        self._flashIconOnChange = config.get(config.FLASH_ICON_ON_CHANGE)

        events.updateCheckCompleted.append(self._showAppUpdateDialog)

    @abstractmethod
    def createApp(self) -> None:
        pass

    def _createCommonMenu(self) -> dict[str, MenuItem]:
        lastTimestamp = Timestamp()
        items = {}

        # Last conversion
        items.update({'last_conversion_label': MenuItem('Last conversion - click to copy', True)})
        items.update({
            self._menuIdLastConversionOriginalText:
                MenuItem(
                    self._formatter.format(lastTimestamp, self._menuTemplateLastConversionOriginalText),
                    callback=self._onMenuClickLastTimestamp,
                ),
        })
        items.update({
            self._menuIdLastConversionConvertedText:
                MenuItem(
                    self._formatter.format(lastTimestamp, self._menuTemplateLastConversionConvertedText),
                    callback=self._onMenuClickLastTimestamp,
                ),
        })
        items.update({'last_conversion_separator': MenuItem(isSeparator=True)})

        # Current timestamp
        if len(self._menuTemplatesCurrentTimestamp) != 0:
            items.update({'current_timestamp_label': MenuItem('Current timestamp - click to copy', True)})

            for key, template in self._menuTemplatesCurrentTimestamp.items():
                items.update({
                    key: MenuItem(key, callback=self._onMenuClickCurrentTimestamp)
                })

            items.update({'current_timestamp_separator': MenuItem(isSeparator=True)})

        # Other controls
        items.update({
            'clear_statusbar': MenuItem('Clear statusbar', callback=self._onMenuClickClearStatusbar),
            'edit_config': MenuItem('Edit configuration', callback=self._onMenuClickEditConfiguration),
            'autostart': MenuItem(
                'Run at login',
                initialState=self._autostartManager.isEnabledAutostart(),
                callback=self._onMenuClickRunAtLogin,
            ),
            'check_updates': MenuItem('Check for updates', callback=self._onMenuClickCheckUpdates),
            'settings': MenuItem('Settings', callback=self._onMenuClickSettings),
        })

        if self._debug.isDebugEnabled():
            items.update({'gui_demo': MenuItem('Open GUI demo', callback=self._onMenuClickOpenGUIDemo)})

        items.update({
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
    def _showAppUpdateDialog(self, version: str | None) -> None:
        pass

    @abstractmethod
    def _onMenuClickLastTimestamp(self, menuItem) -> None:
        pass

    @abstractmethod
    def _onMenuClickCurrentTimestamp(self, menuItem) -> None:
        pass

    def _onMenuClickClearStatusbar(self, menuItem) -> None:
        self._conversionManager.dispatchClear('manual, menu click')

    @abstractmethod
    def _onMenuClickEditConfiguration(self, menuItem) -> None:
        pass

    @abstractmethod
    def _onMenuClickRunAtLogin(self, menuItem) -> None:
        pass

    def _onMenuClickCheckUpdates(self, menuItem) -> None:
        self._updateManager.checkForUpdatesAsync(True)

    def _onMenuClickSettings(self, menuItem) -> None:
        self._modalWindowManager.openModal(ModalId.settings)

    def _onMenuClickOpenGUIDemo(self, menuItem) -> None:
        self._modalWindowManager.openModal(ModalId.demo)

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

    @abstractmethod
    def _showDialog(self, message: str, buttons: list | dict) -> str:
        """Create a dialog window

        @param message: Main message. Can contain formatting on Linux. See supported
            formatting example: https://python-gtk-3-tutorial.readthedocs.io/en/latest/label.html#example
        @param buttons:

        @return: Clicked button name. On macOS dialog window can time out and then
            empty string will be returned
        """
        pass
