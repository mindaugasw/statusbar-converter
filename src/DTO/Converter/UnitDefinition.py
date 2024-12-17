from typing import TypeVar, Generic

from src.DTO.Converter.AbstractUnit import AbstractUnit

UnitDefT = TypeVar('UnitDefT', bound=AbstractUnit)

class UnitDefinition(Generic[UnitDefT]):
    aliases: list[str]
    unit: UnitDefT

    def __init__(self, aliases: list[str], unit: UnitDefT):
        self.aliases = aliases
        self.unit = unit
