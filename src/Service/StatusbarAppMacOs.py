import os
import sys
import threading
import time

import rumps

from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.DTO.ConvertResult import ConvertResult
from src.DTO.MenuItem import MenuItem
from src.DTO.Timestamp import Timestamp
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Conversion.ConversionManager import ConversionManager
from src.Service.Conversion.Converter.Timestamp.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Debug import Debug
from src.Service.EventService import EventService
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.ModalWindowManager import ModalWindowManager
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.UpdateManager import UpdateManager
from src.Type.Types import DialogButtonsDict


class StatusbarAppMacOs(StatusbarApp):
    _app: rumps.App

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        conversionManager: ConversionManager,
        events: EventService,
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
            events,
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
        self._events.subscribeConverted(self._onConverted)
        self._events.subscribeStatusbarClear(self._onStatusbarClear)

        menu = self._createOsNativeMenu(self._createCommonMenu())

        self._app = rumps.App(
            AppConstant.APP_NAME,
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

    def _showAppUpdateDialog(self, text: str, buttons: DialogButtonsDict) -> None:
        text = text.replace('\n', '\\n')
        self._showDialogLegacy(text, buttons)

    def _onMenuClickLastTimestamp(self, menuItem: rumps.MenuItem) -> None:
        self._clipboard.setClipboardContent(menuItem.title)

    def _onMenuClickCurrentTimestamp(self, menuItem: rumps.MenuItem) -> None:
        template = self._menuTemplatesCurrentTimestamp[menuItem.title]
        text = self._formatter.format(Timestamp(), template)

        self._clipboard.setClipboardContent(text)

    def _onMenuClickRunAtLogin(self, menuItem: rumps.MenuItem) -> None:
        if menuItem.state:
            success = self._autostartManager.disableAutostart()
        else:
            success = self._autostartManager.enableAutostart()

        if success:
            menuItem.state = not menuItem.state

    def _onMenuClickRestart(self, menuItem) -> None:
        os.execl(sys.executable, '-m src.main', *sys.argv)

    def _onMenuClickQuit(self, menuItem) -> None:
        # On macOS quit is handled automatically by rumps
        raise Exception('Not implemented')

    def _onConverted(self, result: ConvertResult) -> None:
        if self._flashIconOnChange:
            threading.Thread(target=self._flashIcon, daemon=True).start()

        self._logger.logDebug(Logs.changingIconTextTo % result.iconText)
        self._app.title = result.iconText

        self._menuItems[self._MENU_ID_LAST_CONVERSION_ORIGINAL_TEXT].nativeItem.title = result.originalText
        self._menuItems[self._MENU_ID_LAST_CONVERSION_CONVERTED_TEXT].nativeItem.title = result.convertedText

    def _flashIcon(self) -> None:
        self._app.icon = self._iconPathFlash
        time.sleep(StatusbarAppMacOs._ICON_FLASH_DURATION)
        self._app.icon = self._iconPathDefault

    def _onStatusbarClear(self) -> None:
        self._app.title = None

    def _showDialogDpg(self, text: str, buttons: DialogButtonsDict) -> None:
        # Note that both rumps and dpg dialogs must be initiated from the main UI thread (rumps thread).
        # So it's impossible to use this method after async operation.
        #
        # Trying to show dpg after async update check:
        # NSInternalInconsistencyException, reason: NSWindow should only be instantiated on the main thread!

        super()._showDialogDpg(text, buttons)

    def _showDialogLegacy(self, message: str, buttons: DialogButtonsDict) -> None:
        # Note that both rumps and dpg dialogs must be initiated from the main UI thread (rumps thread).
        # So for async operations this legacy method should be used.

        buttonNames = list(buttons.keys())
        buttonsText = '", "'.join(buttonNames)
        dialogCommand =\
            f'osascript -e \'Tell application "System Events" to display dialog ' \
            f'"{message}" ' \
            f'with title "{AppConstant.APP_NAME}" ' \
            f'buttons {{"{buttonsText}"}} ' \
            f'default button "{buttonNames[0]}" ' \
            f'with icon POSIX file "{self._iconPathDefault}" ' \
            f'giving up after 90\''

        # "giving up after" clause would not be needed, but after 120 seconds
        # AppleEvent timeouts with an exception.
        # So to prevent that we put on a limit to automatically dismiss the dialog

        result = os.popen(dialogCommand).read().strip()

        if 'gave up:true' in result:
            return

        for replaceText in ['button returned:', ', gave up:false', ', gave up:true']:
            result = result.replace(replaceText, '')

        buttonCallback = buttons.get(result)

        if buttonCallback is not None:
            buttonCallback()
