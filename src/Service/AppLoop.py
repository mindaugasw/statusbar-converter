import threading
import time
import src.events as events


class AppLoop:
    LOOP_INTERVAL = 0.33

    def startLoop(self) -> None:
        threading.Thread(target=self._processIteration).start()

    def _processIteration(self) -> None:
        while True:
            events.appLoopIteration()
            time.sleep(AppLoop.LOOP_INTERVAL)
