import dearpygui.demo as demo

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class DemoBuilder(ModalWindowBuilderInterface):
    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Demo',
            'Demo',
            800,
            800,
        )

    def build(self) -> None:
        demo.show_demo()
