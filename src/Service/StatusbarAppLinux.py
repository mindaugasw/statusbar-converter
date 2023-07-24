import gi
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp

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
"""


class StatusbarAppLinux(StatusbarApp):
    def createApp(self) -> None:
        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.new
        # Icons can be also used from `/usr/share/icons`, e.g. 'clock-app'
        indicator = AppIndicator3.Indicator.new(
            'com.mindaugasw.statusbar_converter',
            FilesystemHelper.getAssetsDir() + '/icon_linux.png',
            # TODO try other categories
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )

        # Enable the indicator
        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.set_status
        indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Set text shown on the statusbar (''), and size reservation (None)
        # https://lazka.github.io/pgi-docs/#AyatanaAppIndicator3-0.1/classes/Indicator.html#AyatanaAppIndicator3.Indicator.set_label
        indicator.set_label('', '')
        indicator.set_menu(Gtk.Menu())
        indicator.set_menu(self._createMenuItems())

        Gtk.main()

    def _createMenuItems(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        menuItem1 = Gtk.MenuItem('Item 1')
        # activate = item click
        menuItem1.connect('activate', lambda: self._debug.log('item 1 click'))

        menu.append(menuItem1)
        menu.show_all()

        return menu
