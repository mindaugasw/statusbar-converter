from typing_extensions import Final


class Rounder:
    _MAX_DECIMAL_SPACES: Final = 5

    _levels = {
        # minimum number size => decimal places
        0.00001: 5,
        0.0001: 4,
        0.01: 3,
        0.1: 2,
        1: 2,
        10: 1,
        100: 0,
    }.items()

    _currencyLevels = {
        0.00001: 5,
        0.0001: 4,
        0.001: 3,
        0.01: 2,
        1: 2,
        1000: 0,
    }.items()

    def round(self, number: float) -> str:
        return self._round(number, self._levels)

    def roundCurrency(self, number: float) -> str:
        return self._round(number, self._currencyLevels)

    def _round(self, number: float, levels) -> str:
        decimalPlaces = self._getDecimalPlaces(number, levels)
        number = round(number, decimalPlaces)

        text = f'{number:{decimalPlaces}f}'
        text = text.rstrip('0').rstrip('.')

        if text == '-0':
            text = '0'

        return  text

    def _getDecimalPlaces(self, number: float, levels) -> int:
        number = abs(number)

        for minSize, decimalPlaces in reversed(levels):
            if number >= minSize:
                return decimalPlaces

        return self._MAX_DECIMAL_SPACES
