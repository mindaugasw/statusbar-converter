from src.DTO.Converter.AbstractUnit import AbstractUnit


class CurrencyUnit(AbstractUnit):
    rate: float
    name: str
    category: str

    def __init__(
        self,
        primaryAlias: str,
        prettyFormat: str,
        rate: float,
        name: str,
        category: str,
    ):
        super().__init__(primaryAlias, prettyFormat)

        self.rate = rate
        self.name = name
        self.category = category
