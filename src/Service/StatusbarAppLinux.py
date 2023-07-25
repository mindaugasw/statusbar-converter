import threading
import time
import gi
import signal
import src.events as events
from src.Entity.Timestamp import Timestamp
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
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

Other menu alternatives, instead of using Gtk directly:
- Pystray - much simpler and easier to use, supports all 3 OS: Linux, macOS, Windows.
    Likely much better portability than using Gtk directly.
    But setting icon text/title is bugged and completely doesn't work. 
"""


class StatusbarAppLinux(StatusbarApp):
    _app: AppIndicator3.Indicator

    def __init__(
        self,
        formatter: TimestampTextFormatter,
        config: Configuration,
        debug: Debug,
    ):
        super().__init__(formatter, config, debug)

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
        self._app.set_menu(Gtk.Menu())
        self._app.set_menu(self._createMenuItems())

        # Needed because without this the app exits with errors on app close
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        Gtk.main()

    def _createMenuItems(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        menuItem1 = Gtk.MenuItem('Item 1')
        # activate = item click
        menuItem1.connect('activate', lambda: self._debug.log('item 1 click'))

        menu.append(menuItem1)
        menu.show_all()

        return menu

    def _onTimestampChange(self, timestamp: Timestamp) -> None:
        title = self._formatter.formatForIcon(timestamp)
        self._debug.log(f'Changing statusbar to: {title}')
        self._app.set_label(title, '')

        if self._flashIconOnChange:
            threading.Thread(target=self._flashIcon).start()

    def _flashIcon(self) -> None:
        self._app.set_icon(FilesystemHelper.getAssetsDir() + '/icon_linux_flash.png')
        time.sleep(StatusbarAppLinux.ICON_FLASH_DURATION)
        self._app.set_icon(FilesystemHelper.getAssetsDir() + '/icon_linux.png')

    def _onTimestampClear(self) -> None:
        self._app.set_label('', '')
