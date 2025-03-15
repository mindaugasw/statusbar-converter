import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class DemoBuilder(ModalWindowBuilderInterface):
    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Demo',
            'Demo',
            800,
            800,
            None,
        )

    def reinitializeState(self) -> None:
        pass

    def build(self, arguments: dict[str, any]) -> None:
        demo.show_demo()
        dpg.set_item_pos('__demo_id', [0, 0])
