import threading
import time
import src.events as events
from src.Service.ClipboardManager import ClipboardManager


class AppLoop:
    LOOP_INTERVAL = 0.33

    _clipboardManager: ClipboardManager

    def __init__(self, clipboardManager: ClipboardManager):
        self._clipboardManager = clipboardManager

    def startLoop(self) -> None:
        threading.Thread(target=self._processIteration).start()

    def _processIteration(self) -> None:
        while True:
            events.appLoopIteration()
            time.sleep(self.LOOP_INTERVAL)
