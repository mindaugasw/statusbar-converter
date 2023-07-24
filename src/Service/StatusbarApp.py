from abc import ABCMeta, abstractmethod
from src.Service.Debug import Debug


class StatusbarApp(metaclass=ABCMeta):
    APP_NAME = 'Statusbar Converter'
    ICON_FLASH_DURATION = 0.35

    _debug: Debug

    def __init__(self, debug: Debug):
        self._debug = debug

    @abstractmethod
    def createApp(self) -> None:
        pass
