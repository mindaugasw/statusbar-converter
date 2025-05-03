from typing import Any, Final

import dearpygui.dearpygui as dpg

from src.Constant.AppConstant import AppConstant
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class AboutBuilder(ModalWindowBuilderInterface):
    _PRIMARY_TAG: Final[str] = 'primary'

    _filesystemHelper: FilesystemHelper
    _config: Configuration

    def __init__(self, filesystemHelper: FilesystemHelper, config: Configuration):
        self._filesystemHelper = filesystemHelper
        self._config = config

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'About',
            'About',
            540,
            165,
            self._PRIMARY_TAG,
        )

    def reinitializeState(self) -> None:
        pass

    def build(self, arguments: dict[str, Any]) -> None:
        BuilderHelper.registerHyperlinkTheme()

        with dpg.window(tag=self._PRIMARY_TAG, on_close=self._onClose):

            # group with `horizontal` to make 2 "columns" for image and text
            with dpg.group(horizontal=True):
                with dpg.group():
                    BuilderHelper.addImage(self._filesystemHelper.getAssetsDir() + '/icon_linux.png')

                with dpg.group():
                    dpg.add_text(AppConstant.APP_NAME)
                    dpg.add_text('v' + self._config.getAppVersion())
                    dpg.add_text()

                    with dpg.group(horizontal=True):
                        dpg.add_text('Website:')
                        BuilderHelper.addHyperlink(AppConstant.WEBSITE.replace('https://', ''), AppConstant.WEBSITE)

                    with dpg.group(horizontal=True):
                        dpg.add_text('App icon made by')
                        BuilderHelper.addHyperlink('iconsax at flaticon.com', 'https://www.flaticon.com/free-icons/convert')

    def _onClose(self) -> None:
        BuilderHelper.deleteHyperlinkTheme()
