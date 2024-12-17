import copy

from src.DTO.Converter.AbstractUnit import AbstractUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition, UnitDefT


class UnitPreprocessor:
    def expandAliases(self, units: dict[str, UnitDefinition[UnitDefT]]) -> dict[str, UnitDefT]:
        unitsExpanded: dict[str, AbstractUnit] = {}

        for _, unitDef in units.items():
            primaryAlias = self._cleanString(unitDef.unit.primaryAlias)

            unitExpanded = copy.deepcopy(unitDef.unit)
            unitExpanded.primaryAlias = primaryAlias

            unitsExpanded.update({primaryAlias: unitExpanded})

            for alias in unitDef.aliases:
                aliasCleaned = self._cleanString(alias)

                if aliasCleaned in unitsExpanded:
                    raise Exception(f'Unit alias collision: {aliasCleaned} alias already exists')

                unitsExpanded.update({aliasCleaned: unitExpanded})

        return unitsExpanded

    def _cleanString(self, string: str) -> str:
        return string.lower().replace(' ', '')
