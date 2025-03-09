import os
import shutil
import subprocess
import threading

from src.Constant.ModalId import ModalId
from src.Service.ClipboardManager import ClipboardManager
from src.Service.EventService import EventService
from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
from src.Service.Logger import Logger
from src.Service.ModalWindow.ModalWindowManager import ModalWindowManager


class ClipboardManagerLinux(ClipboardManager):
    _modalWindowManager: ModalWindowManager

    _clipnotifyPath: str

    def __init__(self, events: EventService, logger: Logger, modalWindowManager: ModalWindowManager):
        super().__init__(events, logger)

        self._modalWindowManager = modalWindowManager

        self._clipnotifyPath = FilesystemHelperLinux.getBinariesDir() + '/clipnotify/clipnotify'

        if not os.path.isfile(self._clipnotifyPath):
            raise Exception('Clipnotify binary not found in: ' + self._clipnotifyPath)

    def validateSystem(self) -> bool:
        if shutil.which('xsel') is not None:
            return True

        self._modalWindowManager.openModal(ModalId.missingXsel)

        return False

    def initializeClipboardWatch(self) -> None:
        threading.Thread(target=self._watchClipboard, daemon=True).start()

    def setClipboardContent(self, content: str) -> None:
        subprocess.run(['xsel', '-ib'], input=content, text=True)
        subprocess.run(['xsel', '-ip'], input=content, text=True)

    def _watchClipboard(self) -> None:
        while True:
            # Clipnotify will block thread until selection changes, so we run command and simply wait.
            # To allow clipnotify to block, it must be run with `call`
            # See https://stackoverflow.com/a/2562292/4110469

            subprocess.call([self._clipnotifyPath], stdout=None, stderr=None)

            selection = os.popen('xsel -o').read()

            self._handleChangedClipboard(selection)
