import os
import subprocess
import threading
from src.Service.ClipboardManager import ClipboardManager
from src.Service.FilesystemHelperLinux import FilesystemHelperLinux


class ClipboardManagerLinux(ClipboardManager):
    def initializeClipboardWatch(self) -> None:
        threading.Thread(target=self._watchClipboard, daemon=True).start()

    def setClipboardContent(self, content: str) -> None:
        # TODO this still seems to sometimes not work nicely together with xsel detec
        subprocess.run(['xsel', '-ib'], input=content, text=True)
        subprocess.run(['xsel', '-ip'], input=content, text=True)

    def _watchClipboard(self) -> None:
        clipnotifyPath = FilesystemHelperLinux.getBinariesDir() + '/clipnotify/clipnotify'

        while True:
            # Clipnotify will block thread until selection changes, so we run command and simply wait.
            # To allow clipnotify to block, it must be run with `call`
            # See https://stackoverflow.com/a/2562292/4110469
            subprocess.call([clipnotifyPath], stdout=None, stderr=None)

            selection = os.popen('xsel -o').read()
            # selection = os.popen('xsel -obp').read()

            self._handleChangedClipboard(selection)
