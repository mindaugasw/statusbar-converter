import subprocess
import sys
import threading
import time
import webbrowser
import gi
import signal
import src.events as events
from src.Entity.MenuItem import MenuItem
from src.Entity.Timestamp import Timestamp
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.AutostartManager import AutostartManager
from src.Service.UpdateManager import UpdateManager

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3


"""
AppIndicator tutorial 1: https://fosspost.org/custom-system-tray-icon-indicator-linux/
Tutorial 2: https://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html
Usage examples: https://www.programcreek.com/python/example/103466/gi.repository.AppIndicator3

Documentation: 
- https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1
    From https://askubuntu.com/a/1315648/1152277
    Preferred documentation. In settings use filter to show only `AyatanaAppIndicator3 0.1` and `Gtk 3.0`

- `libappindicator-doc` package
    From https://askubuntu.com/a/1019338/1152277
    Access at file:///usr/share/gtk-doc/html/libappindicator/index.html
    
- https://launchpad.net/stackapplet
    https://bazaar.launchpad.net/~george-edison55/stackapplet/trunk/view/head:/src/stackapplet.py
    More usage examples, including some undocumented features

- https://python-gtk-3-tutorial.readthedocs.io/en/latest/label.html#example
    Advanced text formatting example

Other menu alternatives, instead of using Gtk directly:
- Pystray - much simpler and easier to use, supports all 3 OS: Linux, macOS, Windows.
    Likely much better portability than using Gtk directly.
    But setting icon text/title is bugged and completely doesn't work.
    See experimental StatusbarAppPystray in git history.
"""


class StatusbarAppLinux(StatusbarApp):
    CHECK = '✔  '

    _app: AppIndicator3.Indicator

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        config: Configuration,
        configFileManager: ConfigFileManager,
        autostartManager: AutostartManager,
        updateManager: UpdateManager,
        debug: Debug,
    ):
        super().__init__(
            osSwitch,
            formatter,
            clipboard,
            config,
            configFileManager,
            autostartManager,
            updateManager,
            debug,
        )

        self._iconPathDefault = FilesystemHelper.getAssetsDir() + '/icon_linux.png'
        self._iconPathFlash = FilesystemHelper.getAssetsDir() + '/icon_linux_flash.png'

    def createApp(self) -> None:
        events.timestampChanged.append(self._onTimestampChange)
        events.timestampClear.append(self._onTimestampClear)

        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.new
        self._app = AppIndicator3.Indicator.new(
            StatusbarAppLinux.APP_NAME,
            # Icons can be also used from `/usr/share/icons`, e.g. 'clock-app'
            FilesystemHelper.getAssetsDir() + '/icon_linux.png',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )

        self._app.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self._app.set_label('', '')
        menu = self._createOsNativeMenu(self._createCommonMenu())
        self._app.set_menu(menu)

        # Needed because without this the app exits with errors on app close
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        Gtk.main()

    def _createOsNativeMenu(self, commonMenu: dict[str, MenuItem]) -> Gtk.Menu:
        menu = Gtk.Menu()

        item: MenuItem
        for key, item in commonMenu.items():
            if item.isSeparator:
                nativeItem = Gtk.SeparatorMenuItem()
                menu.append(nativeItem)

                continue

            nativeItem = Gtk.MenuItem(item.label)

            if item.initialState:
                """
                There is a Gtk.CheckMenuItem, but we don't use it because we
                can't completely control check behavior then:
                - button state is automatically changed by Gtk before calling callback
                - if we then manually change state again, button callback is called again
                So simulating check behavior with text is simpler
                """

                nativeItem.set_label(f'{self.CHECK}{item.label}')

            if item.isDisabled:
                nativeItem.set_sensitive(False)

            if item.callback:
                nativeItem.connect('activate', item.callback)

            item.setNativeItem(nativeItem)
            menu.append(nativeItem)

        menu.show_all()

        return menu

    def _showAppUpdateDialog(self, version: str | None) -> None:
        if version is None:
            self._showDialog(
                f'No new version found.\n'
                f'Current app version is v{self._config.getAppVersion()}.',
                ['Ok'],
            )

            return

        buttons = {
            'download': 'Download update',
            'skip': 'Skip this version',
            'later': 'Remind me later',
        }
        downloadPage = f'{StatusbarAppLinux.WEBSITE}/releases/tag/{version}'

        result = self._showDialog(
            f'New app update found: {version}.\n'
            f'Current app version is v{self._config.getAppVersion()}.\n'
            f'Release notes available on the <a href="{downloadPage}">download page</a>.\n\n'
            f'Download update?',
            buttons,
        )

        self._debug.log(f'Update check: user action: {result}')

        if result == buttons['download']:
            webbrowser.open(downloadPage)
        elif result == buttons['skip']:
            self._config.setState(Configuration.DATA_UPDATE_SKIP_VERSION, version)
        elif result == buttons['later']:
            return
        else:
            self._debug.log(f'Update check: unknown user action: {result}')

    def _onMenuClickLastTimestamp(self, menuItem: Gtk.MenuItem) -> None:
        label = menuItem.get_label()
        self._clipboard.setClipboardContent(label)

    def _onMenuClickCurrentTimestamp(self, menuItem: Gtk.MenuItem) -> None:
        template = self._menuTemplatesCurrentTimestamp[menuItem.get_label()]
        text = self._formatter.format(Timestamp(), template)

        self._clipboard.setClipboardContent(text)

    def _onMenuClickEditConfiguration(self, menuItem: Gtk.MenuItem | None) -> None:
        buttons = {
            'open': 'Open in default editor',
            'close': 'Cancel',
        }

        response = self._showDialog(
            f'Configuration can be edited in the file: \n'
            f'<tt>{self._configFilePath}</tt>\n\n'
            f'After editing, the application must be restarted.\n\n'
            f'All supported configuration can be found at:\n'
            f'<a href="{StatusbarAppLinux.WEBSITE}">{StatusbarAppLinux.WEBSITE}</a>\n\n'
            f'Open configuration file in default text editor?',
            buttons,
        )

        if response == buttons['open']:
            subprocess.call(['xdg-open', self._configFilePath])

    def _onMenuClickRunAtLogin(self, menuItem: Gtk.MenuItem) -> None:
        checked = self._isMenuItemChecked(menuItem)

        if checked:
            self._autostartManager.disableAutostart()
            success = True
        else:
            success = self._autostartManager.enableAutostart()

        if success:
            menuItem.set_label(f'{"" if checked else self.CHECK}Run at login')

    def _onMenuClickOpenWebsite(self, menuItem: Gtk.MenuItem) -> None:
        webbrowser.open(StatusbarAppLinux.WEBSITE)

    def _onMenuClickAbout(self, menuItem: Gtk.MenuItem) -> None:
        self._showDialog(
            f'Version: {self._config.getAppVersion()}\n\n'
            f'App website: <a href="{StatusbarAppLinux.WEBSITE}">{StatusbarAppLinux.WEBSITE}</a>\n\n'
            f'App icon made by <a href="https://www.flaticon.com/free-icons/convert">iconsax at flaticon.com</a>',
            ['Ok'],
        )

    def _onMenuClickQuit(self, menuItem) -> None:
        Gtk.main_quit()
        sys.exit()

    def _onTimestampChange(self, timestamp: Timestamp) -> None:
        # Icon flash must be first action. Otherwise, it's visible how text is
        # updated first and icon later, and looks bad
        if self._flashIconOnChange:
            threading.Thread(target=self._flashIcon, daemon=True).start()

        iconLabel = self._formatter.formatForIcon(timestamp)
        self._debug.log(f'Changing statusbar to: {iconLabel}')
        self._app.set_label(iconLabel, '')

        for key, template in self._menuTemplatesLastTimestamp.items():
            lastTimestampLabel = self._formatter.format(timestamp, template)
            self._menuItems[key].nativeItem.set_label(lastTimestampLabel)

            # There was a bug where it seems like menu items were not being
            # actually updated when changing them too fast. So adding this
            # delay hoping it'll fix it
            time.sleep(0.1)

    def _flashIcon(self) -> None:
        self._app.set_icon(FilesystemHelper.getAssetsDir() + '/icon_linux_flash.png')
        time.sleep(StatusbarAppLinux.ICON_FLASH_DURATION)
        self._app.set_icon(FilesystemHelper.getAssetsDir() + '/icon_linux.png')

    def _onTimestampClear(self) -> None:
        self._app.set_label('', '')

    def _showDialog(self, message: str, buttons: list | dict) -> str:
        if isinstance(buttons, dict):
            buttons = list(buttons.values())

        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.OTHER,
            buttons=Gtk.ButtonsType.NONE,
            text=StatusbarAppLinux.APP_NAME,
        )

        dialog.format_secondary_markup(message)

        for i, button in enumerate(buttons):
            dialog.add_button(button, i)

        response = dialog.run()
        dialog.destroy()

        return buttons[response]

    def _isMenuItemChecked(self, menuItem: Gtk.MenuItem) -> bool:
        return menuItem.get_label().startswith(self.CHECK)
