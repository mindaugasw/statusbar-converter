from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface


class UnitParseResult:
    number: float
    unit: str
    converter: SimpleConverterInterface

    def __init__(
        self,
        number: float,
        unit: str,
        converter: SimpleConverterInterface,
    ):
        self.number = number
        self.unit = unit
        self.converter = converter
