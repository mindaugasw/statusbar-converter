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
        parameters = builder.getParameters()
        logCategory = Logs.catModal + parameters.logCategory + '] '
        self._logger.logDebug(logCategory + 'Initialize')

        dpg.create_context()
        dpg.create_viewport(
            title=AppConstant.appName + ' - ' + parameters.title,
            width=parameters.width,
            height=parameters.height,
        )

        builder.build()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        self._logger.logDebug(logCategory + 'Start')
        dpg.start_dearpygui()
        self._logger.logDebug(logCategory + 'Closed')
        dpg.destroy_context()
        self._logger.logDebug(logCategory + 'Destroyed')
