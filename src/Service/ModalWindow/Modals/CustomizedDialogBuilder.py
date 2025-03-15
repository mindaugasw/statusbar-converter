from collections.abc import Callable

import dearpygui.dearpygui as dpg

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class CustomizedDialogBuilder(ModalWindowBuilderInterface):
    _primaryTag = 'primary'
    _minimumNewLines = 8
    _callbacks: dict[str | int, Callable | None]

    def __init__(self):
        super().__init__()

        self._callbacks = {}

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            None,
            'Dialog',
            500,
            198,
            self._primaryTag,
        )

    def build(self, arguments: dict[str, any]) -> None:
        text = arguments['text']
        buttons = arguments['buttons']
        buildCallback: Callable[None, None] | None = arguments.get('buildCallback')

        # There are no proper tools in dpg for vertical alignment. So we fake it by setting
        # text height to always the same by adding more lines, to reach minimum count
        linesInText = text.count('\n') + 1
        text += '\n ' * (self._minimumNewLines - linesInText)

        with dpg.window(tag=self._primaryTag, autosize=True):
            with dpg.group(horizontal=True):
                with dpg.group():
                    BuilderHelper.addImage(FilesystemHelper.getAssetsDir() + '/icon_colored_small.png')

                with dpg.group():
                    if buildCallback is not None:
                        buildCallback()
                    else:
                        dpg.add_text(text)

            dpg.add_separator()

            with dpg.group():
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    for buttonText, buttonCallback in buttons.items():
                        """
                        There is a bug that `callback` argument is assigned to ALL buttons. So all
                        buttons call the callback of the last assigned button, instead of the one
                        that was actually assigned to that button. We work around this by having a
                        property dictionary with actual callbacks.
                        """

                        text = BuilderHelper.padButtonText(buttonText)
                        tag = dpg.add_button(label=text, height=25, callback=self._handleButtonPress)
                        self._callbacks[tag] = buttonCallback

    def _handleButtonPress(self, sender: str | int, appData, userData) -> None:
        if self._callbacks[sender] is not None:
            self._callbacks[sender]()

        dpg.stop_dearpygui()
