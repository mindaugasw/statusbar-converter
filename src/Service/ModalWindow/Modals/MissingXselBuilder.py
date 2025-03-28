from typing import Any

import dearpygui.dearpygui as dpg

from src.Constant.AppConstant import AppConstant
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.Modals.CustomizedDialogBuilder import CustomizedDialogBuilder
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class DialogMissingXselBuilder(ModalWindowBuilderInterface):
    _customizedDialogBuilder: CustomizedDialogBuilder

    def __init__(self, customizedDialogBuilder: CustomizedDialogBuilder):
        super().__init__()

        self._customizedDialogBuilder = customizedDialogBuilder

    def getParameters(self) -> ModalWindowParameters:
        parameters = self._customizedDialogBuilder.getParameters()
        parameters.height = 198

        return parameters

    def reinitializeState(self) -> None:
        self._customizedDialogBuilder.reinitializeState()

    def build(self, arguments: dict[str, Any]) -> None:
        self._customizedDialogBuilder.build({
            'text': '',
            'buttons': {'Close': None},
            'buildCallback': lambda: self._buildInternal()
        })

    def _buildInternal(self) -> None:
        text =\
            f'Could not start {AppConstant.APP_NAME}.\n' \
            'Package "xsel" is missing from your system.\n\n' \
            'Run the following command and start the app again:'

        dpg.add_text(text)
        dpg.add_input_text(default_value='sudo apt-get install xsel', readonly=True)
        dpg.add_text('\n\n')
