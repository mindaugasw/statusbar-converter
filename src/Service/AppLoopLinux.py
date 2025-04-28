import time

from src.Service.AppLoop import AppLoop


class AppLoopLinux(AppLoop):
    def _processIteration(self) -> None:
        while True:
            self._events.dispatchAppLoopIteration()
            time.sleep(self._SLOW_LOOP_INTERVAL)
