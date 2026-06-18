import time


class Timestamp:
    seconds: int
    milliseconds: int | None

    def __init__(self, seconds: int | None = None, milliseconds: int | None = None):
        if seconds is None:
            seconds = int(time.time())

        self.seconds = seconds
        self.milliseconds = milliseconds

    def __str__(self) -> str:
        return self.toString(True, '.')

    def toString(self, includeMs=True, msSeparator='.') -> str:
        if self.milliseconds is None or not includeMs:
            return str(self.seconds)

        return f'{self.seconds}{msSeparator}{self.milliseconds:03d}'
