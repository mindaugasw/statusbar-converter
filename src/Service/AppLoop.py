import threading
import time
import src.events as events
from src.Service.OSSwitch import OSSwitch


class AppLoop:
    _osSwitch: OSSwitch

    _loopInterval: float

    def __init__(self, osSwitch: OSSwitch):
        self._osSwitch = osSwitch

    def startLoop(self) -> None:
        # On macOS AppLoop is used for clipboard polling, so we must keep interval
        # short. On Linux there's no critical tasks attached to AppLoop, so we can
        # make interval way longer
        self._loopInterval = 0.33 if self._osSwitch.isMacOS() else 5

        threading.Thread(target=self._processIteration).start()

    def _processIteration(self) -> None:
        while True:
            events.appLoopIteration()
            time.sleep(self._loopInterval)
