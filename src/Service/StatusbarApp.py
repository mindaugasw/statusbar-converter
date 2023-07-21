from abc import ABCMeta, abstractmethod


class StatusbarApp(metaclass=ABCMeta):
    # TODO move to macOS class?
    # On macOS this name will be used in Application Support directory for this app
    APP_NAME = 'Statusbar Converter'

    def createApp(self) -> None:
        pass
