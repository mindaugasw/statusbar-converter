import dearpygui.dearpygui as dpg

from src.Constant.AppConstant import AppConstant
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface


class AboutBuilder(ModalWindowBuilderInterface):
    _primaryTag = 'primary'

    _config: Configuration

    def __init__(self, config: Configuration):
        self._config = config

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'About',
            'About',
            530,
            150,
            self._primaryTag,
        )

    def build(self) -> None:
        BuilderHelper.registerHyperlinkTheme()

        with dpg.window(label='Window title', tag=self._primaryTag, on_close=self._onClose):

            # group with `horizontal` to make 2 "columns" for image and text
            with dpg.group(horizontal=True):
                with dpg.group():
                    width, height, channels, data = dpg.load_image(FilesystemHelper.getAssetsDir() + '/icon_linux.png')

                    with dpg.texture_registry():
                        dpg.add_static_texture(
                            width=width,
                            height=height,
                            default_value=data,
                            tag='image',
                        )

                    dpg.add_image('image')

                with dpg.group():
                    dpg.add_text(AppConstant.appName)
                    dpg.add_text('v' + self._config.getAppVersion())
                    dpg.add_text()

                    with dpg.group(horizontal=True):
                        dpg.add_text('Website:')
                        BuilderHelper.hyperlink(AppConstant.website.replace('https://', ''), AppConstant.website)

                    with dpg.group(horizontal=True):
                        dpg.add_text('App icon made by')
                        BuilderHelper.hyperlink('iconsax at flaticon.com', 'https://www.flaticon.com/free-icons/convert')

    def _onClose(self) -> None:
        BuilderHelper.deleteHyperlinkTheme()
