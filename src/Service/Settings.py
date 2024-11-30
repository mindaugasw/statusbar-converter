import threading
from typing import Callable

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.Service.Logger import Logger
from src.Service.OSSwitch import OSSwitch


class Settings:
    _osSwitch: OSSwitch
    _logger: Logger

    def __init__(self, osSwitch: OSSwitch, logger: Logger):
        self._osSwitch = osSwitch
        self._logger = logger

    def openGUIDemo(self) -> None:
        def _buildGUIDemoWindow() -> None:
            self._logger.logDebug(Logs.catSettingsDemo + 'Initialize')

            dpg.create_context()
            dpg.create_viewport(title=AppConstant.appName + ' - GUI demo', width=800, height=800)
            demo.show_demo()

            dpg.setup_dearpygui()
            dpg.show_viewport()
            self._logger.logDebug(Logs.catSettingsDemo + 'Start')
            dpg.start_dearpygui()
            self._logger.logDebug(Logs.catSettingsDemo + 'Done')
            dpg.destroy_context()
            self._logger.logDebug(Logs.catSettingsDemo + 'Destroyed')

        self._showWindow(_buildGUIDemoWindow)

    def openSettings(self) -> None:
        def _buildSettingsWindow() -> None:
            self._logger.logDebug(Logs.catSettings + 'Initialize')

            dpg.create_context()
            dpg.create_viewport(title=AppConstant.appName + ' - Settings', width=600, height=300)

            with dpg.window(label='Window title'):
                dpg.add_text('Hello world')

            dpg.setup_dearpygui()
            dpg.show_viewport()
            self._logger.logDebug(Logs.catSettings + 'Start')
            dpg.start_dearpygui()
            self._logger.logDebug(Logs.catSettings + 'Closed')
            dpg.destroy_context()
            self._logger.logDebug(Logs.catSettings + 'Destroyed')

        self._showWindow(_buildSettingsWindow)

    def _showWindow(self, builderCallback: Callable) -> None:
        if self._osSwitch.isLinux():
            # On Linux dpg UI is blocking, so we start it in a thread to allow other events to still function.
            # Thread must be non-daemon for that to work.
            # Some functions can still crash the app. E.g. opening GTK popup ("About") when settings are open
            threading.Thread(target=builderCallback).start()

            return

        # On macOS dpg UI seems to be non-blocking. Copy events are processed even with dpg open directly from
        # rumps thread. Opening in a separate thread does not work on macOS, crashes saying that it must run
        # from main thread
        builderCallback()
