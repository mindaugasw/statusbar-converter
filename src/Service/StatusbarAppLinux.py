import threading
import time
import gi
import signal
import src.events as events
from src.Entity.MenuItem import MenuItem
from src.Entity.Timestamp import Timestamp
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampTextFormatter import TimestampTextFormatter

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
- `libappindicator-doc` package
    From https://askubuntu.com/a/1019338/1152277
    Access at file:///usr/share/gtk-doc/html/libappindicator/index.html
- https://launchpad.net/stackapplet
    https://bazaar.launchpad.net/~george-edison55/stackapplet/trunk/view/head:/src/stackapplet.py
    More usage examples, including some undocumented features

Other menu alternatives, instead of using Gtk directly:
- Pystray - much simpler and easier to use, supports all 3 OS: Linux, macOS, Windows.
    Likely much better portability than using Gtk directly.
    But setting icon text/title is bugged and completely doesn't work. 
"""


class StatusbarAppLinux(StatusbarApp):
    _app: AppIndicator3.Indicator

    def __init__(
        self,
        osSwitch: OSSwitch,
        formatter: TimestampTextFormatter,
        clipboard: ClipboardManager,
        config: Configuration,
        debug: Debug,
    ):
        super().__init__(osSwitch, formatter, clipboard, config, debug)

        self._iconPathDefault = FilesystemHelper.getAssetsDir() + '/icon_linux.png'
        self._iconPathFlash = FilesystemHelper.getAssetsDir() + '/icon_linux_flash.png'

    def createApp(self) -> None:
        events.timestampChanged.append(self._onTimestampChange)
        events.timestampClear.append(self._onTimestampClear)

        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.new
        self._app = AppIndicator3.Indicator.new(
            'com.mindaugasw.statusbar_converter',
            # Icons can be also used from `/usr/share/icons`, e.g. 'clock-app'
            FilesystemHelper.getAssetsDir() + '/icon_linux.png',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )

        # Enable the indicator
        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.set_status
        self._app.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Set text shown on the statusbar
        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.set_label
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

            if item.isDisabled:
                nativeItem.set_sensitive(False)

            if item.callback:
                nativeItem.connect('activate', item.callback)

            item.setNativeItem(nativeItem)
            menu.append(nativeItem)

        menu.show_all()

        return menu

    def _onMenuClickLastTimestamp(self, menuItem: Gtk.MenuItem) -> None:
        label = menuItem.get_label()
        self._clipboard.setClipboardContent(label)

    def _onMenuClickCurrentTimestamp(self, menuItem: Gtk.MenuItem) -> None:
        template = self._menuTemplatesCurrentTimestamp[menuItem.get_label()]
        text = self._formatter.format(Timestamp(), template)

        self._clipboard.setClipboardContent(text)

    def _onMenuClickClearTimestamp(self, menuItem: Gtk.MenuItem) -> None:
        events.timestampClear()

    def _onMenuClickQuit(self, menuItem) -> None:
        Gtk.main_quit()
        exit()

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
