from collections.abc import Callable
from typing import Any, Final

import dearpygui.dearpygui as dpg

from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Type.Types import DpgTag


class CustomizedDialogBuilder(ModalWindowBuilderInterface):
    _PRIMARY_TAG: Final[str] = 'primary'
    _MINIMUM_NEW_LINES: Final[int] = 8

    _callbacks: dict[DpgTag, Callable | None]

    def __init__(self):
        super().__init__()

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            None,
            'Dialog',
            500,
            198,
            self._PRIMARY_TAG,
        )

    def reinitializeState(self) -> None:
        self._callbacks = {}

    def build(self, arguments: dict[str, Any]) -> None:
        text = arguments['text']
        buttons = arguments['buttons']
        buildCallback: Callable[[], None] | None = arguments.get('buildCallback')

        # There are no proper tools in dpg for vertical alignment. So we fake it by setting
        # text height to always the same by adding more lines, to reach minimum count
        linesInText = text.count('\n') + 1
        text += '\n ' * (self._MINIMUM_NEW_LINES - linesInText)

        with dpg.window(tag=self._PRIMARY_TAG, autosize=True):
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

    def _handleButtonPress(self, sender: DpgTag, appData, userData) -> None:
        callback = self._callbacks[sender]

        if callback is not None:
            callback()

        dpg.stop_dearpygui()
