from abc import ABC


class AbstractUnit(ABC):
    primaryAlias: str
    prettyFormat: str

    def __init__(self, primaryAlias: str, prettyFormat: str):
        self.primaryAlias = primaryAlias
        self.prettyFormat = prettyFormat
