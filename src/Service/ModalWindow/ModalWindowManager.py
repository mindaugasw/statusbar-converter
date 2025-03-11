import threading

import dearpygui.dearpygui as dpg
import dearpygui_ext.themes

from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.Constant.ModalId import ModalId
from src.Service.EventService import EventService
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Service.OSSwitch import OSSwitch
from src.Type.DialogButtonsDict import DialogButtonsDict


class ModalWindowManager:
    """
    Based on Dear PyGui

    See docs at: https://dearpygui.readthedocs.io
    """

    _builders: dict[str, ModalWindowBuilderInterface]
    _osSwitch: OSSwitch
    _events: EventService
    _logger: Logger

    _isModalOpen: bool

    def __init__(
        self,
        builders: dict[str, ModalWindowBuilderInterface],
        osSwitch: OSSwitch,
        events: EventService,
        logger: Logger,
    ):
        self._builders = builders
        self._osSwitch = osSwitch
        self._events = events
        self._logger = logger

        self._isModalOpen = False

    def openModal(self, _id: str):
        """
        Open a complex, pre-built UI window
        """
        self._openModalInternal(_id, {})

    def openCustomizedDialog(self, text: str, buttons: DialogButtonsDict):
        """
        Open a simple parameterized UI window with text and multiple buttons
        """
        self._openModalInternal(ModalId.customizedDialog, {'text': text, 'buttons': buttons})

    def _openModalInternal(self,  _id: str, arguments: dict[str, any]):
        if _id not in self._builders:
            raise Exception('Tried opening modal by non-existing id: ' + _id)

        if self._isModalOpen:
            self._logger.logDebug(Logs.catModal + 'Cannot open 2 modals at once, tried opening id: ' + _id)

            return

        self._isModalOpen = True
        self._events.setEventBlocking(True)
        self._showWindow(self._builders[_id], arguments)

    def _showWindow(self, builder: ModalWindowBuilderInterface, arguments: dict[str, any]) -> None:
        if self._osSwitch.isLinux():
            # On Linux, dpg UI is blocking, so we start it in a thread to allow other events to still function.
            # Thread must be non-daemon for that to work.
            # Some functions can still crash the app. E.g. opening GTK popup when settings are open
            threading.Thread(target=lambda: self._buildWindow(builder, arguments)).start()

            return

        # On macOS, dpg UI seems to be non-blocking. Copy events are processed even with dpg open directly from
        # rumps thread. Opening in a separate thread does not work on macOS, crashes saying that it must run
        # from the main thread
        self._buildWindow(builder, arguments)

    def _buildWindow(self, builder: ModalWindowBuilderInterface, arguments: dict[str, any]) -> None:
        parameters = builder.getParameters()
        logCategory = Logs.catModalSub + parameters.logCategory + '] '
        self._logger.logDebug(logCategory + 'Initialize')

        viewportTitle = AppConstant.appName
        if parameters.title is not None:
            viewportTitle = parameters.title + ' - ' + viewportTitle

        dpg.create_context()
        # Viewport is OS-drawn window
        dpg.create_viewport(
            title=viewportTitle,
            width=parameters.width,
            height=parameters.height,
            # To position window at the center, we assume standard 1920x1080 resolution.
            # Getting actual resolution is too complicated for very little benefit.
            # dpg will always place window within monitor bounds, even if given position exceeds resolution.
            x_pos=int(1920 / 2 - parameters.width / 2),
            y_pos=int(1080 / 2 - parameters.height / 2) - 200,
            min_width=parameters.width,
            max_width=parameters.width,
            min_height=parameters.height,
            max_height=parameters.height,
            resizable=False,
        )

        with dpg.font_registry():
            defaultFont = dpg.add_font(FilesystemHelper.getAssetsDir() + '/font_supreme_regular.otf', 18)
            dpg.bind_font(defaultFont)

        # Build dpg-window - one that appears inside the viewport
        builder.build(arguments)

        dpg.bind_theme(dearpygui_ext.themes.create_theme_imgui_dark())
        dpg.setup_dearpygui()
        dpg.show_viewport()

        if parameters.primaryWindowTag:
            dpg.set_primary_window(parameters.primaryWindowTag, True)

        self._logger.logDebug(logCategory + 'Start')
        dpg.start_dearpygui()

        dpg.destroy_context()
        self._logger.logDebug(logCategory + 'Closed')

        self._isModalOpen = False
        self._events.setEventBlocking(False)
