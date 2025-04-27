from src.DTO.Converter.AbstractUnit import AbstractUnit


class CurrencyUnit(AbstractUnit):
    def __init__(
        self,
        primaryAlias: str,
        prettyFormat: str,
        rate: float,
    ):
        super().__init__(primaryAlias, prettyFormat)
