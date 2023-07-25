from abc import ABCMeta, abstractmethod
from src.Entity.MenuItem import MenuItem
from src.Entity.Timestamp import Timestamp
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.OSSwitch import OSSwitch
from src.Service.TimestampTextFormatter import TimestampTextFormatter


class StatusbarApp(metaclass=ABCMeta):
    APP_NAME = 'Statusbar Converter'
    ICON_FLASH_DURATION = 0.35

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

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        config: Configuration,
        debug: Debug,
    ):
        self._osSwitch = osSwitch
        self._formatter = formatter
        self._clipboard = clipboard
        self._debug = debug

        self._menuTemplatesLastTimestamp = config.get(config.MENU_ITEMS_LAST_TIMESTAMP)
        self._menuTemplatesCurrentTimestamp = config.get(config.MENU_ITEMS_CURRENT_TIMESTAMP)
        self._flashIconOnChange = config.get(config.FLASH_ICON_ON_CHANGE)

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
            'edit_config': MenuItem('Edit configuration'),
            'open_website': MenuItem('Open website'),
            'restart': MenuItem('Restart application'),
        })

        # On macOS Quit button is automatically created by rumps app
        if self._osSwitch.isLinux():
            items.update({
                'quit': MenuItem('Quit', callback=self._onMenuClickQuit)
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

    @abstractmethod
    def _onMenuClickClearTimestamp(self, menuItem) -> None:
        pass

    def _onMenuClickQuit(self, menuItem) -> None:
        pass
