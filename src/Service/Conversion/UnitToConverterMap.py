from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface


class UnitToConverterMap:
    _map: dict[str, SimpleConverterInterface]

    def __init__(self, converters: list[SimpleConverterInterface]):
        self._map = self._generateMap(converters)

    def __getitem__(self, unitId: str) -> SimpleConverterInterface:
        return self._map[unitId]

    def __contains__(self, item: str) -> bool:
        return item in self._map

    def __len__(self) -> int:
        return len(self._map)

    def _generateMap(self, converters: list[SimpleConverterInterface]) -> dict[str, SimpleConverterInterface]:
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
