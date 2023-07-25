from abc import ABCMeta, abstractmethod
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.TimestampTextFormatter import TimestampTextFormatter


class StatusbarApp(metaclass=ABCMeta):
    APP_NAME = 'Statusbar Converter'
    ICON_FLASH_DURATION = 0.35

    _formatter: TimestampTextFormatter
    _debug: Debug

    _iconPathDefault: str
    _iconPathFlash: str
    _flashIconOnChange: bool

    def __init__(
        self,
        formatter: TimestampTextFormatter,
        config: Configuration,
        debug: Debug,
    ):
        self._formatter = formatter
        self._debug = debug

        self._flashIconOnChange = config.get(config.FLASH_ICON_ON_CHANGE)

    @abstractmethod
    def createApp(self) -> None:
        pass
