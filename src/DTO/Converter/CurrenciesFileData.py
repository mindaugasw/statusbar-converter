class CurrenciesFileData:
    refreshedAt: int
    cachedAt: int
    currencies: dict

    def __init__(self, refreshedAt: int, cachedAt: int, currencies: dict):
        self.refreshedAt = refreshedAt
        self.cachedAt = cachedAt
        self.currencies = currencies
