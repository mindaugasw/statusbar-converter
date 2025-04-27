from typing import Final


class UnitPosition:
    """During unit conversion, unit position relative to number (before $5, or after 5$)"""

    BEFORE: Final = 'before'
    AFTER: Final = 'after'
