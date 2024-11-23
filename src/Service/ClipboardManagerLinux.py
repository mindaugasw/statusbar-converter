import os
import subprocess
import threading
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Debug import Debug
from src.Service.FilesystemHelperLinux import FilesystemHelperLinux


class ClipboardManagerLinux(ClipboardManager):
    _clipnotifyPath: str

    def __init__(self, debug: Debug):
        super().__init__(debug)

        self._clipnotifyPath = FilesystemHelperLinux.getBinariesDir() + '/clipnotify/clipnotify'

        if not os.path.isfile(self._clipnotifyPath):
            raise Exception('Clipnotify binary not found in: ' + self._clipnotifyPath)

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
            # selection = os.popen('xsel -obp').read()

            self._handleChangedClipboard(selection)
