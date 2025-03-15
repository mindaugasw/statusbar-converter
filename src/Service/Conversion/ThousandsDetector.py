import re
from typing import Final


class ThousandsDetector:
    """
    Responsible for detecting thousands separator vs decimal separator in a number.
    E.g. what number is 1,234.567 and what number is 100,500 ?
    """

    _PATTERN_CONFUSION_DOT_THOUSANDS: Final = re.compile(
        r'^(?:[-+]?(?=.*\d)(?=.*[1-9]).{1,3}\.\d{3})$',  # for numbers like '100.000' (is it 100.0 or 100000?)
    )
    _PATTERN_CONFUSION_COMMA_THOUSANDS: Final = re.compile(
        r'^(?:[-+]?(?=.*\d)(?=.*[1-9]).{1,3},\d{3})$',  # for numbers like '100,000' (is it 100.0 or 100000?)
    )
    _PATTERN_COMMA_THOUSANDS_DOT_DECIMAL: Final = re.compile(r'^[-+]?((\d{1,3}(,\d{3})*)|(\d*))(\.|\.\d*)?$')
    _PATTERN_DOT_THOUSANDS_COMMA_DECIMAL: Final = re.compile(r'^[-+]?((\d{1,3}(\.\d{3})*)|(\d*))(,|,\d*)?$')

    def parseNumber(self, number: str) -> float | None:
        """
        Algorithm source: https://stackoverflow.com/a/55518600/4110469
        """

        number = number.strip().lstrip('0')

        if number == '':
            # If number is '0', the lstrip() above will return empty string
            number = '0'

        # "certain" - concept from algorithm source. Not needed currently, since there's no "max value"
        # certain = True

        if self._PATTERN_CONFUSION_DOT_THOUSANDS.match(number) is not None:
            number = number.replace('.', '')  # assume dot is thousands separator
            # certain = False
        elif self._PATTERN_CONFUSION_COMMA_THOUSANDS.match(number) is not None:
            number = number.replace(',', '')  # assume comma is thousands separator
            # certain = False
        elif self._PATTERN_COMMA_THOUSANDS_DOT_DECIMAL.match(number) is not None:
            number = number.replace(',', '')
        elif self._PATTERN_DOT_THOUSANDS_COMMA_DECIMAL.match(number) is not None:
            number = number.replace('.', '').replace(',', '.')
        else:
            # For stuff like '10,000.000,0' and other nonsense
            return None

        numberFloat = float(number)

        # if not certain and max_val is not None and number > max_val:
        #     number *= 0.001  # Change previous assumption to decimal separator, so '100.000' goes from 100000.0 to 100.0
        #     certain = True  # Since this uniquely satisfies the given constraint, it should be a certainly correct interpretation

        return numberFloat
