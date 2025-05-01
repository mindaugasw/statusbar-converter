from src.DTO.Converter.CurrenciesFileData import CurrenciesFileData


class CurrenciesRefreshResult:
    success: bool
    isOutdated: bool
    data: CurrenciesFileData | None

    def __init__(self, success: bool, isOutdated: bool, data: CurrenciesFileData | None = None):
        self.success = success
        self.isOutdated = isOutdated
        self.data = data
