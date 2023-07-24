from abc import ABCMeta, abstractmethod


class StatusbarApp(metaclass=ABCMeta):
    APP_NAME = 'Statusbar Converter'

    # TODO add abstract?
    def createApp(self) -> None:
        pass
