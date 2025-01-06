from collections.abc import Callable

import dearpygui.dearpygui as dpg

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class DialogBuilder(ModalWindowBuilderInterface):
    _primaryTag = 'primary'
    _minimumNewLines = 7
    _callbacks: dict[str | int, Callable | None]

    def __init__(self):
        super().__init__()

        self._callbacks = {}

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            None,
            'Dialog',
            450,
            145,
            self._primaryTag,
        )

    def build(self, arguments: dict[str, any]) -> None:
        text = arguments['text']
        buttons = arguments['buttons']

        # There are no proper tools in dpg for vertical alignment. So we fake it by setting
        # text height to always the same by adding more lines, to reach minimum count
        linesInText = text.count('\n') + 1
        text += '\n ' * (self._minimumNewLines - linesInText)

        with dpg.window(tag=self._primaryTag, autosize=True):
            # TODO add app logo to the right.
            # Like in "About" modal, but smaller. Without any image, the modal looks very dark. Small font requires actually reading it
            with dpg.group():
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
                        tag = dpg.add_button(label=buttonText, height=25, callback=self._handleButtonPress)
                        self._callbacks[tag] = buttonCallback

    def _handleButtonPress(self, sender: str | int, appData, userData) -> None:
        if self._callbacks[sender] is not None:
            self._callbacks[sender]()

        dpg.stop_dearpygui()
