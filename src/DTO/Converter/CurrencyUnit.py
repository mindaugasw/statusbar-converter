from src.DTO.Converter.AbstractUnit import AbstractUnit


class CurrencyUnit(AbstractUnit):
    rate: float
    name: str
    category: str

    def __init__(
        self,
        primaryAlias: str,
        prettyFormat: str, # TODO when converting, use pretty format only if it's the main currency. Otherwise, primary alias. Or maybe apply this only for submenu header? Or make only exceptions for $/€?
        rate: float,
        name: str,
        category: str,
    ):
        super().__init__(primaryAlias, prettyFormat)

        self.rate = rate
        self.name = name
        self.category = category
