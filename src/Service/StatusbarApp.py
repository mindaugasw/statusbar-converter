from abc import ABCMeta, abstractmethod


class StatusbarApp(metaclass=ABCMeta):
    APP_NAME = 'Statusbar Converter'

    def createApp(self) -> None:
        pass
