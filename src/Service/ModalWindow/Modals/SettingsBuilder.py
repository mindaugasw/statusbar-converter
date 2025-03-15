from typing import Callable, Any, Final, Type

import dearpygui.dearpygui as dpg

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.DTO.SettingsControlProperties import SettingsControlProperties
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Type.Types import DpgTag


class SettingsBuilder(ModalWindowBuilderInterface):
    _WINDOW_WIDTH: Final[int] = 600
    _PRIMARY_TAG: Final[str] = 'primary'

    _SPACER_LEFT_INDENT_WIDTH: Final[int] = 1
    _SPACER_SECTION_TOP_HEIGHT: Final[int] = 3

    _config: Configuration
    _logger: Logger

    _controls: dict[DpgTag, SettingsControlProperties]
    _appRestartNoteDefaultTag: DpgTag
    _appRestartNoteEditedTag: DpgTag
    _appRestartNoteChanged: bool

    def __init__(self, config: Configuration, logger: Logger):
        self._config = config
        self._logger = logger

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Settings',
            'Settings',
            self._WINDOW_WIDTH,
            600,
            self._PRIMARY_TAG,
        )

    def reinitializeState(self) -> None:
        self._controls = {}
        self._appRestartNoteDefaultTag = -1
        self._appRestartNoteEditedTag = -1
        self._appRestartNoteChanged = False

    def build(self, arguments: dict[str, Any]) -> None:
        with dpg.window(label='Window title', tag=self._PRIMARY_TAG):
            self._buildHeader()
            self._buildGeneralSettings()
            self._buildFooter()

    def _buildHeader(self) -> None:
        with dpg.group(horizontal=True):
            with dpg.group():
                BuilderHelper.addImage(FilesystemHelper.getAssetsDir() + '/icon_colored_small.png')

            with dpg.group():
                dpg.add_text('Settings')
                dpg.add_text('v' + self._config.getAppVersion(), pos=[self._WINDOW_WIDTH - 50, 8])

                dpg.add_spacer(height=5)

                # Seems like it's impossible to change text color. So we create 2 labels, 1 hidden, and then switch them
                noteText = 'App needs to be restarted for changes to take effect.'
                self._appRestartNoteDefaultTag = dpg.add_text(noteText)
                self._appRestartNoteEditedTag = dpg.add_text(noteText, show=False, color=(255, 0, 0, 255))

                dpg.add_spacer(height=25)

    def _buildGeneralSettings(self) -> None:
        dpg.add_separator(label='General settings')

        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_spacer(width=self._SPACER_LEFT_INDENT_WIDTH)

            with dpg.group():
                dpg.add_spacer(height=self._SPACER_SECTION_TOP_HEIGHT)

                self._registerControl(
                    dpg.add_checkbox(label='Flash statusbar icon on successful conversion'),
                    ConfigId.FlashIconOnChange,
                    bool,
                )

                self._registerControl(
                    dpg.add_checkbox(label='Clear statusbar text on clipboard change'),
                    ConfigId.ClearOnChange,
                    bool,
                )

                self._registerControl(
                    dpg.add_input_int(
                        label='Automatically clear statusbar text after this many seconds',
                        width=50,
                        min_value=0,
                        max_value=3600,
                        step=0,
                        step_fast=0,
                        min_clamped=True,
                        max_clamped=True,
                    ),
                    ConfigId.ClearAfterTime,
                    int,
                )
                BuilderHelper.addHelpText('Enter zero to disable automatic text clearing')

    def _buildFooter(self) -> None:
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_spacer(width=self._SPACER_LEFT_INDENT_WIDTH)

            with dpg.group():
                dpg.add_spacer(height=self._SPACER_SECTION_TOP_HEIGHT)

                dpg.add_button(label='Reset all to default')

    def _registerControl(self, tag: DpgTag, configId: ConfigParameter, castToType: Type):
        dpg.set_item_callback(tag, self._controlCallback)
        dpg.set_value(tag, self._config.get(configId))
        self._controls[tag] = SettingsControlProperties(configId, castToType)

    def _controlCallback(self, sender: DpgTag, appData, userData, action: Callable) -> None:
        controlProperties = self._controls[sender]
        value = controlProperties.castToType(appData)

        label = dpg.get_item_label(sender)
        self._logger.log(f'{Logs.catSettings}Callback #{sender} ({label}) with data: {value} ({type(value).__name__})')

        self._config.set(controlProperties.configId, value)

        if self._appRestartNoteChanged is False:
            dpg.hide_item(self._appRestartNoteDefaultTag)
            dpg.show_item(self._appRestartNoteEditedTag)
            self._appRestartNoteChanged = True
