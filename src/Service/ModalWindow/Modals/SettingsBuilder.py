from typing import Callable, Any

import dearpygui.dearpygui as dpg

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class SettingsBuilder(ModalWindowBuilderInterface):
    _config: Configuration
    _logger: Logger

    _windowWidth = 600
    _primaryTag = 'primary'

    _callbacks: dict[int, Callable[[Any], None]]
    _appRestartNoteDefaultTag: int
    _appRestartNoteEditedTag: int
    _appRestartNoteChanged: bool

    def __init__(self, config: Configuration, logger: Logger):
        self._config = config
        self._logger = logger

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Settings',
            'Settings',
            self._windowWidth,
            300,
            self._primaryTag,
        )

    def reinitializeState(self) -> None:
        self._callbacks = {}
        self._appRestartNoteDefaultTag = -1
        self._appRestartNoteEditedTag = -1
        self._appRestartNoteChanged = False

    def build(self, arguments: dict[str, any]) -> None:
        with dpg.window(label='Window title', tag=self._primaryTag):

            with dpg.group(horizontal=True):
                with dpg.group():
                    BuilderHelper.addImage(FilesystemHelper.getAssetsDir() + '/icon_colored_small.png')

                with dpg.group():
                    dpg.add_text('Settings')
                    dpg.add_text('v' + self._config.getAppVersion(), pos=[self._windowWidth - 50, 8])

                    dpg.add_spacer(height=5)

                    # Seems like it's impossible to change text color. So we create 2 labels, 1 hidden, and then switch them
                    noteText = 'App needs to be restarted for changes to take effect.'
                    self._appRestartNoteDefaultTag = dpg.add_text(noteText)
                    self._appRestartNoteEditedTag = dpg.add_text(noteText, show=False, color=(255, 0, 0, 255))

                    dpg.add_spacer(height=25)

            self._buildGeneralSettings()

    def _buildGeneralSettings(self) -> None:
        dpg.add_separator(label='General settings')

        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_spacer(width=1)

            with dpg.group():
                dpg.add_spacer()

                self._callbacks[dpg.add_checkbox(
                    label='Flash statusbar icon on successful conversion',
                    callback=self._controlCallback,
                    default_value=self._config.getState(ConfigId.FlashIconOnChange, True),
                )] = lambda appData: self._config.setState(ConfigId.FlashIconOnChange, bool(appData))

                # TODO next add callback for this
                # TODO test if this works without custom callback
                dpg.add_checkbox(
                    label='Clear statusbar on clipboard change',
                    callback=self._controlCallback,
                )

                dpg.add_button(label='but 1', callback=lambda: print('but 1'))
                dpg.add_button(label='but 2', callback=lambda: print('but 2'))
                dpg.add_button(label='but 3', callback=self._controlCallback)

    def _controlCallback(self, sender: int, appData, userData, action: Callable) -> None:
        label = dpg.get_item_label(sender)

        self._logger.log(f'{Logs.catSettings}Callback #{sender} ({label}) with data: {appData}')

        if self._callbacks[sender] is not None:
            self._callbacks[sender](appData)

        if self._appRestartNoteChanged is False:
            dpg.hide_item(self._appRestartNoteDefaultTag)
            dpg.show_item(self._appRestartNoteEditedTag)
            self._appRestartNoteChanged = True
