import os
import subprocess
import threading
from src.Service.ClipboardManager import ClipboardManager
from src.Service.FilesystemHelperLinux import FilesystemHelperLinux


class ClipboardManagerLinux(ClipboardManager):
    def initializeClipboardWatch(self) -> None:
        threading.Thread(target=self._watchClipboard).start()

    def setClipboardContent(self, content: str) -> None:
        raise Exception('not impl')

    def _watchClipboard(self) -> None:
        clipnotifyPath = FilesystemHelperLinux.getBinariesDir() + '/clipnotify/clipnotify'

        while True:
            #TODO finish, clean up
            # Clipnotify will block thread until selection changes, so we run command and simply wait
            # subprocess.Popen(clipnotifyPath)
            os.popen(clipnotifyPath)

            # To allow clipnotify to block, it must be run with `call`
            # See https://stackoverflow.com/a/2562292/4110469
            subprocess.call([clipnotifyPath], stdout=None, stderr=None)

            selection = os.popen('xsel -o').read()
            # selection = subprocess.check_output(['xsel', '-o'])
            # selection = subprocess.check_output('xsel', universal_newlines=True)
            self._debug.log('Selection changed: ' + selection)
