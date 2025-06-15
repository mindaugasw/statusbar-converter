from src.Constant.UnitPosition import UnitPosition
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Service.EventService import EventService


class UnitToConverterMapper:
    _map: dict[str, dict[str, UnitConverterInterface]]

    def __init__(
        self,
        unitBeforeConverters: list[UnitConverterInterface],
        unitAfterConverters: list[UnitConverterInterface],
        events: EventService,
    ):
        self._map = {
            UnitPosition.BEFORE: self._generateMap(unitBeforeConverters),
            UnitPosition.AFTER: self._generateMap(unitAfterConverters),
        }

        events.subscribeDelayedConverterInitialized(self._onDelayedConverterInitialized)

    def getConverter(self, unit: str, unitPosition: str) -> None | UnitConverterInterface:
        return self._map[unitPosition].get(unit)

    def _generateMap(self, converters: list[UnitConverterInterface]) -> dict[str, UnitConverterInterface]:
        _map: dict[str, UnitConverterInterface] = {}

        for converter in converters:
            if not converter.isEnabled():
                continue

            if converter.isDelayedInitialization():
                continue

            self._appendConverterMap(_map, converter)

        return _map

    def _appendConverterMap(self, _map: dict[str, UnitConverterInterface], converter: UnitConverterInterface) -> None:
        unitIds = converter.getUnitIds()

        for unitId in unitIds:
            if unitId in _map:
                raise Exception(f'Unit alias collision: {unitId} alias already exists')

            _map[unitId] = converter

    def _onDelayedConverterInitialized(self, converter: UnitConverterInterface) -> None:
        # If there will be more delayed converters, this should first check each
        # converter if it exists in before/after list

        self._rebuildMapForDelayedConverter(self._map[UnitPosition.BEFORE], converter)
        self._rebuildMapForDelayedConverter(self._map[UnitPosition.AFTER], converter)

    def _rebuildMapForDelayedConverter(
        self,
        _map: dict[str, UnitConverterInterface],
        converter: UnitConverterInterface,
    ) -> None:
        keysToDelete = [key for key, value in _map.items() if value == converter]

        for key in keysToDelete:
            del _map[key]

        self._appendConverterMap(_map, converter)
