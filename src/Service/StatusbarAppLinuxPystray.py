import random
import threading
import time
from pystray import Icon, Menu, MenuItem
from PIL import Image
import src.events as events
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp

"""
Seems like setting icon text/title is not working. No text appears in any way.
If it would work, it's much simpler and easier to use than gtk directly
"""
# TODO remove and archive

class StatusbarAppLinuxPystray(StatusbarApp):
    _iconImage: Image
    _iconImageFlash: Image
    _iconApp: Icon

    _iconFlashInProgress = False

    def createApp(self) -> None:
        self._iconImage = Image.open(FilesystemHelper.getAssetsDir() + '/icon_linux.png')
        self._iconImageFlash = Image.open(FilesystemHelper.getAssetsDir() + '/icon_linux_flash.png')

        events.clipboardChanged.append(lambda a: self._startIconFlash())

        self._iconApp = Icon(
            name='fxk',
            icon=self._iconImage,
            title='my',
            menu=self._createMenu('1st'),
        )

        self._iconApp.title = 'wtf'

        self._iconApp.run()

    def _createMenu(self, itemName: str) -> Menu:
        itemFlashIcon = MenuItem(
            'Button - ' + itemName,
            self._onClick,
        )

        menu = Menu(itemFlashIcon)

        return menu

    def _onClick(self, icon: Icon, item: MenuItem) -> None:
        randNum = str(random.randrange(9999))
        self._debug.log('clicked ' + randNum)

    def _startIconFlash(self) -> None:
        threading.Thread(target=self._flashIcon).start()

    def _flashIcon(self) -> None:
        if self._iconFlashInProgress:
            return

        self._iconFlashInProgress = True

        randNum = str(random.randrange(9999))
        self._iconApp.title = randNum
        # self._iconApp.update_menu()
        self._iconApp.menu = self._createMenu(randNum)
        self._iconApp.icon = self._iconImageFlash
        time.sleep(StatusbarAppLinuxPystray.ICON_FLASH_DURATION)
        self._iconApp.icon = self._iconImage
        self._debug.log('done')
        self._iconFlashInProgress = False
