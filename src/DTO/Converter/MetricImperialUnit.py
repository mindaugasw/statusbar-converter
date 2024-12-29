from src.DTO.Converter.AbstractUnit import AbstractUnit


class MetricImperialUnit(AbstractUnit):
    isMetric: bool
    convertToThis: bool
    limitToShowUnit: float
    multiplierToBaseUnit: float

    def __init__(
        self,
        primaryAlias: str,
        prettyFormat: str,
        isMetric: bool,
        convertToThis: bool,
        limitToShowUnit: float,
        multiplierToBaseUnit: float,
    ):
        """
        :param primaryAlias:
        :param prettyFormat: Format that will be used when printing text in the statusbar, no matter
            which alias was matched
        :param isMetric:
        :param convertToThis: If false, number will never be converter TO this unit, only from it
        :param limitToShowUnit: When converting TO this unit, if number is higher than this value,
            then the next bigger unit will be selected instead (to show 5 km instead of 5000 m)
        :param multiplierToBaseUnit: Multiplier to the base unit, in metric system.
            E.g. to get meters for any distance unit
        """

        super().__init__(primaryAlias, prettyFormat)

        self.isMetric = isMetric
        self.convertToThis = convertToThis
        self.limitToShowUnit = limitToShowUnit
        self.multiplierToBaseUnit = multiplierToBaseUnit
