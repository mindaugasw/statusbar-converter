class RelativeTimeData:
    diff: int
    """Absolute difference in seconds between given timestamp and now"""

    number: float
    """Relative time amount, e.g. 5.5"""

    unit: str
    """Relative time unit, e.g. 'd'"""

    isPast: bool
    """If timestamp is in the past or in the future"""

    def __init__(self, diff: int, isPast: bool):
        self.diff = diff
        self.isPast = isPast

    def setRelativeTime(self, number: float, unit: str) -> None:
        self.number = number
        self.unit = unit
