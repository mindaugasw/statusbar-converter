import copy

from src.DTO.Converter.AbstractUnit import AbstractUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition, UnitDefT


class UnitPreprocessor:
    @staticmethod
    def expandAliases(units: dict[str, UnitDefinition[UnitDefT]]) -> dict[str, UnitDefT]:
        unitsExpanded: dict[str, AbstractUnit] = {}

        for _, unitDef in units.items():
            primaryAlias = UnitPreprocessor._cleanString(unitDef.unit.primaryAlias)

            unitExpanded = copy.deepcopy(unitDef.unit)
            unitExpanded.primaryAlias = primaryAlias

            unitsExpanded.update({primaryAlias: unitExpanded})

            for alias in unitDef.aliases:
                aliasCleaned = UnitPreprocessor._cleanString(alias)

                if aliasCleaned in unitsExpanded:
                    raise Exception(f'Unit alias collision: {aliasCleaned} alias already exists')

                unitsExpanded.update({aliasCleaned: unitExpanded})

        return unitsExpanded

    @staticmethod
    def pluralizeAliases(aliases: list[str]) -> list[str]:
        newList: list[str] = []

        for alias in aliases:
            newList.append(alias)
            newList.append(alias + 's')

        return newList

    @staticmethod
    def _cleanString(string: str) -> str:
        return string.lower().replace(' ', '')
