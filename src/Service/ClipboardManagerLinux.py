import os
import subprocess
import threading

from src.Service.ClipboardManager import ClipboardManager
from src.Service.EventService import EventService
from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
from src.Service.Logger import Logger


class ClipboardManagerLinux(ClipboardManager):
    _clipnotifyPath: str

    def __init__(self, events: EventService, logger: Logger):
        super().__init__(events, logger)

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

            # TODO use loop mode. Probably should reduce resource usage. See:
            # https://github.com/cdown/clipnotify/commit/c04a22ed5322c3aecf10697a024731ad25a772a8

            subprocess.call([self._clipnotifyPath], stdout=None, stderr=None)

            selection = os.popen('xsel -o').read()
            # selection = os.popen('xsel -obp').read()

            self._handleChangedClipboard(selection)
