import os
import subprocess
import threading
import time
from typing import Callable

import rumps

import src.events as events
from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.DTO.ConvertResult import ConvertResult
from src.DTO.MenuItem import MenuItem
from src.DTO.Timestamp import Timestamp
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.ConversionManager import ConversionManager
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.ModalWindowManager import ModalWindowManager
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.UpdateManager import UpdateManager


class StatusbarAppMacOs(StatusbarApp):
    _app: rumps.App

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
        super().__init__(
            osSwitch,
            formatter,
            clipboard,
            conversionManager,
            config,
            configFileManager,
            autostartManager,
            updateManager,
            modalWindowManager,
            logger,
            debug,
        )

        self._iconPathDefault = FilesystemHelper.getAssetsDir() + '/icon_macos.png'
        self._iconPathFlash = FilesystemHelper.getAssetsDir() + '/icon_macos_flash.png'

    def createApp(self) -> None:
        events.converted.append(self._onConverted)
        events.statusbarClear.append(self._onStatusbarClear)

        menu = self._createOsNativeMenu(self._createCommonMenu())

        self._app = rumps.App(
            AppConstant.appName,
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

            if item.initialState is not None:
                nativeItem.state = item.initialState

            item.setNativeItem(nativeItem)
            menu.update({key: nativeItem})

        return menu

    def _showAppUpdateDialog(self, text: str, buttons: dict[str, Callable | None]) -> None:
        text = text.replace('\n', '\\n')
        self._showDialog(text, buttons)

    def _onMenuClickLastTimestamp(self, menuItem: rumps.MenuItem) -> None:
        self._clipboard.setClipboardContent(menuItem.title)

    def _onMenuClickCurrentTimestamp(self, menuItem: rumps.MenuItem) -> None:
        template = self._menuTemplatesCurrentTimestamp[menuItem.title]
        text = self._formatter.format(Timestamp(), template)

        self._clipboard.setClipboardContent(text)

    def _onMenuClickEditConfiguration(self, menuItem: rumps.MenuItem) -> None:
        buttons = {
            'Open in default editor': lambda: subprocess.Popen(['open', self._configFilePath]),
            'Cancel': None,
        }

        self._showDialog(
            f'Configuration can be edited in the file:\\n'
            f'{self._configFilePath}\\n\\n'
            f'After editing, the application must be restarted.\\n\\n'
            f'All supported configuration can be found at:\\n'
            f'{AppConstant.website}/blob/master/config.app.yml\\n\\n'
            f'Open configuration file in default text editor?',
            buttons,
        )

    def _onMenuClickRunAtLogin(self, menuItem: rumps.MenuItem) -> None:
        if menuItem.state:
            self._autostartManager.disableAutostart()
            success = True
        else:
            success = self._autostartManager.enableAutostart()

        if success:
            menuItem.state = not menuItem.state

    # TODO remove
    def _onMenuClickAboutOld(self, menuItem: rumps.MenuItem) -> None:
        self._showDialog(
            f'Version: {self._config.getAppVersion()}\\n\\n'
            f'App website: {AppConstant.website}\\n\\n'
            f'App icon made by iconsax at flaticon.com',
            {'Ok': None},
        )

    def _onConverted(self, result: ConvertResult) -> None:
        if self._flashIconOnChange:
            threading.Thread(target=self._flashIcon, daemon=True).start()

        self._logger.logDebug(Logs.changingIconTextTo % result.iconText)
        self._app.title = result.iconText

        self._menuItems[self._menuIdLastConversionOriginalText].nativeItem.title = result.originalText
        self._menuItems[self._menuIdLastConversionConvertedText].nativeItem.title = result.convertedText

    def _flashIcon(self) -> None:
        self._app.icon = self._iconPathFlash
        time.sleep(StatusbarAppMacOs.ICON_FLASH_DURATION)
        self._app.icon = self._iconPathDefault

    def _onStatusbarClear(self) -> None:
        self._app.title = None

    def _showDialog(self, message: str, buttons: dict[str, Callable | None]) -> None:
        # Here rumps dialog cannot be shown because it's initiated from a different thread.
        # And can't be initiated from the main thread because of async request.
        # Also, automatic update check can't trigger dialog from rumps main thread.
        # Same problem with dpg.
        # So we're using non-rumps and non-dpg dialog

        buttonNames = list(buttons.keys())
        buttonsText = '", "'.join(buttonNames)
        dialogCommand =\
            f'osascript -e \'Tell application "System Events" to display dialog ' \
            f'"{message}" ' \
            f'with title "{AppConstant.appName}" ' \
            f'buttons {{"{buttonsText}"}} ' \
            f'default button "{buttonNames[0]}" ' \
            f'with icon POSIX file "{self._iconPathDefault}" ' \
            f'giving up after 60\''

        # "giving up after" clause would not be needed, but after 120 seconds
        # AppleEvent timeouts with an exception.
        # So to prevent that we put on a limit to automatically dismiss the dialog

        result = os.popen(dialogCommand).read().strip()

        for replaceText in ['button returned:', ', gave up:false', ', gave up:true']:
            result = result.replace(replaceText, '')

        buttonCallback = buttons[result]

        if buttonCallback is not None:
            buttonCallback()
