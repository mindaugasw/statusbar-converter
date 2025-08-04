from abc import ABC, abstractmethod
from typing import Tuple

from src.DTO.ConvertResult import ConvertResult
from src.DTO.Converter.MetricImperialUnit import MetricImperialUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.Service.Conversion.Rounder import Rounder
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Service.Conversion.Unit.UnitPreprocessor import UnitPreprocessor


class AbstractMetricImperialConverter(UnitConverterInterface, ABC):
    _rounder: Rounder

    _enabled: bool
    _maxValueBaseUnit: float
    _minValueBaseUnit: float
    _primaryUnitMetric: bool
    _unitsDefinition: dict[str, UnitDefinition[MetricImperialUnit]]
    _unitsExpanded: dict[str, MetricImperialUnit]

    def __init__(
        self,
        rounder: Rounder,
        enabled: bool,
        primaryUnitMetric: bool,
        maxValueBaseUnit: float,
        minValueBaseUnit: float,
    ):
        self._rounder = rounder
        self._enabled = enabled
        self._maxValueBaseUnit = maxValueBaseUnit
        self._minValueBaseUnit = minValueBaseUnit
        self._primaryUnitMetric = primaryUnitMetric
        self._unitsDefinition = self._getUnitsDefinition()
        self._unitsExpanded = UnitPreprocessor.expandAliases(self._unitsDefinition)

    def isEnabled(self) -> bool:
        return self._enabled

    def isDelayedInitialization(self) -> bool:
        return False

    def getUnitIds(self) -> list[str]:
        if not self._enabled:
            raise Exception(f'Cannot getUnitIds for disabled {self.getName()} converter')

        return list(self._unitsExpanded.keys())

    def tryConvert(self, number: float, unitId: str) -> Tuple[bool, ConvertResult | None]:
        unitFrom = self._unitsExpanded[unitId]

        if unitFrom.isMetric == self._primaryUnitMetric:
            return False, None

        meters = number * unitFrom.multiplierToBaseUnit
        metersAbs = abs(meters)

        if metersAbs > self._maxValueBaseUnit or metersAbs < self._minValueBaseUnit:
            return False, None

        numberTo: float = -1
        unitTo: MetricImperialUnit | None = None

        for _, unitDef in self._unitsDefinition.items():
            unitIteration = unitDef.unit

            if unitIteration.isMetric != self._primaryUnitMetric or not unitIteration.convertToThis:
                continue

            numberTo = meters / unitIteration.multiplierToBaseUnit

            if abs(numberTo) >= unitIteration.limitToShowUnit:
                continue

            unitTo = unitIteration

            break

        numberFromRounded = self._rounder.round(number)
        numberToRounded = self._rounder.round(numberTo)

        textFrom = f'{numberFromRounded} {unitFrom.prettyFormat}'
        textTo = f'{numberToRounded} {unitTo.prettyFormat}'  # type: ignore[union-attr]

        return True, ConvertResult(f'{textFrom}  =  {textTo}', textFrom, textTo, self.getName())

    @abstractmethod
    def _getUnitsDefinition(self) -> dict[str, UnitDefinition[MetricImperialUnit]]:
        pass
