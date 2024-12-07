class UnitPreprocessor:
    # TODO define DTOs for units instead of using dicts
    def process(self, units: dict) -> dict:
        unitsProcessed = {}

        for _id, unit in units.items():
            primaryId = self._cleanString(_id)

            unitsProcessed.update({primaryId: {'primaryId': primaryId}})

            for alias in unit['aliases']:
                aliasId = self._cleanString(alias)
                unitsProcessed.update({aliasId: {'primaryId': primaryId}})

        return unitsProcessed

    def _cleanString(self, string: str) -> str:
        return string.lower().replace(' ', '')
