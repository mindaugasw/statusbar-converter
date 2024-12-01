import dearpygui.dearpygui as dpg

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class SettingsBuilder(ModalWindowBuilderInterface):
    _primaryTag = 'primary'

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Settings',
            'Settings',
            600,
            300,
            self._primaryTag,
        )

    def build(self, arguments: dict[str, any]) -> None:
        with dpg.window(label='Window title', tag=self._primaryTag):
            dpg.add_text('Hello world')
