import dearpygui.dearpygui as dpg

from src.Constant.AppConstant import AppConstant
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.DialogBuilder import DialogBuilder
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class DialogMissingXselBuilder(ModalWindowBuilderInterface):
    _dialogBuilder: DialogBuilder

    def __init__(self, dialogBuilder: DialogBuilder):
        super().__init__()

        self._dialogBuilder = dialogBuilder

    def getParameters(self) -> ModalWindowParameters:
        parameters = self._dialogBuilder.getParameters()
        parameters.height = 198

        return parameters

    def build(self, arguments: dict[str, any]) -> None:
        self._dialogBuilder.build({
            'text': '',
            'buttons': {'Close': None},
            'buildCallback': lambda: self._buildInternal()
        })

    def _buildInternal(self) -> None:
        text =\
            f'Could not start {AppConstant.appName}.\n' \
            'Package "xsel" is missing from your system.\n\n' \
            'Run the following command and start the app again:'

        dpg.add_text(text)
        dpg.add_input_text(default_value='sudo apt-get install xsel', readonly=True)
        dpg.add_text('\n\n')
