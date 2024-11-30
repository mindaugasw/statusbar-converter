import threading

import dearpygui.dearpygui as dpg

from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.Service.Logger import Logger
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Service.OSSwitch import OSSwitch


class ModalWindowManager:
    _builders: dict[str, ModalWindowBuilderInterface]
    _osSwitch: OSSwitch
    _logger: Logger

    _isModalOpen = False

    def __init__(
        self,
        builders: dict[str, ModalWindowBuilderInterface],
        osSwitch: OSSwitch,
        logger: Logger,
    ):
        self._builders = builders
        self._osSwitch = osSwitch
        self._logger = logger

    def openModal(self, _id: str):
        if _id not in self._builders:
            raise Exception('Tried opening modal by non-existing id: ' + _id)

        if self._isModalOpen:
            self._logger.logDebug(Logs.catModal + 'Cannot open 2 modals at once, tried opening id: ' + _id)

            return

        self._isModalOpen = True
        self._showWindow(self._builders[_id])

    def _showWindow(self, builder: ModalWindowBuilderInterface) -> None:
        if self._osSwitch.isLinux():
            # On Linux, dpg UI is blocking, so we start it in a thread to allow other events to still function.
            # Thread must be non-daemon for that to work.
            # Some functions can still crash the app. E.g. opening GTK popup when settings are open
            threading.Thread(target=lambda: self._buildWindow(builder)).start()

            return

        # On macOS, dpg UI seems to be non-blocking. Copy events are processed even with dpg open directly from
        # rumps thread. Opening in a separate thread does not work on macOS, crashes saying that it must run
        # from the main thread
        self._buildWindow(builder)

    def _buildWindow(self, builder: ModalWindowBuilderInterface) -> None:
        """
        See docs at https://dearpygui.readthedocs.io
        """

        parameters = builder.getParameters()
        logCategory = Logs.catModalSub + parameters.logCategory + '] '
        self._logger.logDebug(logCategory + 'Initialize')

        dpg.create_context()
        # Viewport is OS-drawn window
        dpg.create_viewport(
            title=AppConstant.appName + ' - ' + parameters.title,
            width=parameters.width,
            height=parameters.height,
            min_width=parameters.width,
            max_width=parameters.width,
            min_height=parameters.height,
            max_height=parameters.height,
            resizable=False,
        )

        # Build dpg-window - one that appears inside the viewport
        builder.build()

        dpg.setup_dearpygui()
        dpg.show_viewport()

        if parameters.primaryWindowTag:
            dpg.set_primary_window(parameters.primaryWindowTag, True)

        self._logger.logDebug(logCategory + 'Start')
        dpg.start_dearpygui()
        self._logger.logDebug(logCategory + 'Closed')
        dpg.destroy_context()
        self._logger.logDebug(logCategory + 'Destroyed')

        self._isModalOpen = False