from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface


class UnitToConverterMap:
    _map: dict[str, UnitConverterInterface]

    def __init__(self, converters: list[UnitConverterInterface]):
        self._map = self._generateMap(converters)

    def __getitem__(self, unitId: str) -> UnitConverterInterface:
        return self._map[unitId]

    def __contains__(self, item: str) -> bool:
        return item in self._map

    def __len__(self) -> int:
        return len(self._map)

    def _generateMap(self, converters: list[UnitConverterInterface]) -> dict[str, UnitConverterInterface]:
        _map = {}

        for converter in converters:
            if not converter.isEnabled():
                continue

            unitIds = converter.getUnitIds()

            for unitId in unitIds:
                if unitId in _map:
                    raise Exception(f'Unit alias collision: {unitId} alias already exists')

                _map[unitId] = converter

        return _map
