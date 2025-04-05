from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface


class UnitParseResult:
    number: float
    unit: str
    converter: UnitConverterInterface

    def __init__(
        self,
        number: float,
        unit: str,
        converter: UnitConverterInterface,
    ):
        self.number = number
        self.unit = unit
        self.converter = converter
