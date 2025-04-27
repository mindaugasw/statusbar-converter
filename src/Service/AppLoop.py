import threading
import time

from src.Service.EventService import EventService
from src.Service.OSSwitch import OSSwitch


class AppLoop:
    _osSwitch: OSSwitch
    _events: EventService

    _loopInterval: float

    def __init__(self, osSwitch: OSSwitch, events: EventService):
        self._osSwitch = osSwitch
        self._events = events

    def startLoop(self) -> None:
        # On macOS AppLoop is used for clipboard polling, so we must keep interval
        # short. On Linux there's no critical tasks attached to AppLoop, so we can
        # make interval way longer
        # TODO split this into appLoopFast and appLoopSlow
        self._loopInterval = 0.33 if self._osSwitch.isMacOS() else 5

        threading.Thread(target=self._processIteration, daemon=True).start()

    def _processIteration(self) -> None:
        while True:
            self._events.dispatchAppLoopIteration()
            time.sleep(self._loopInterval)
