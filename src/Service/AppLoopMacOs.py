import time

from src.Service.AppLoop import AppLoop
from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
from src.Service.EventService import EventService


class AppLoopMacOs(AppLoop):
    _clipboardManager: ClipboardManagerMacOs

    def __init__(
        self,
        events: EventService,
        clipboardManager: ClipboardManagerMacOs,
    ):
        super().__init__(events)

        self._clipboardManager = clipboardManager

    def _processIteration(self) -> None:
        # On macOS AppLoop is used for clipboard polling, so we introduce 2 loops:
        # fast one for polling, and slower one for all other tasks

        iterationsForSlowLoop = int(self._SLOW_LOOP_INTERVAL / 0.33)
        fastLoopIterations = 0

        while True:
            # Here skipping event system and calling directly to optimize as much as possible a frequently running loop
            self._clipboardManager.pollClipboard()

            if fastLoopIterations > iterationsForSlowLoop:
                self._events.dispatchAppLoopIteration()
                fastLoopIterations = 0

            fastLoopIterations += 1

            time.sleep(0.33)
