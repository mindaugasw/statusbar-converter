import dearpygui.dearpygui as dpg

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class SettingsBuilder(ModalWindowBuilderInterface):
    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Settings',
            'Settings',
            600,
            300,
        )

    def build(self) -> None:
        with dpg.window(label='Window title'):
            dpg.add_text('Hello world')
