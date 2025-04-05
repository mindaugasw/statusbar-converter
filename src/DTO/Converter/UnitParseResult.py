class UnitParseResult:
    isSuccess: bool
    number: float
    unit: str
    unitGroup: int

    def __init__(self, number: float, unit: str, unitGroup: int):
        self.isSuccess = True
        self.number = number
        self.unit = unit
        self.unitGroup = unitGroup
