import math
import webbrowser
from typing import Callable, Any

import dearpygui.dearpygui as dpg
from typing_extensions import Final


class BuilderHelper:
    COLOR_TEXT_BLUE: Final = [29, 151, 236]

    _HYPERLINK_THEME_TAG: Final[str] = '_app_hyperlink_theme'

    @staticmethod
    def registerHyperlinkTheme() -> None:
        """
        Hyperlink code from dpg demo.py
        """
        dpg.add_texture_registry(label='_app_texture_container', tag='_app_texture_container')

        with dpg.theme(tag=BuilderHelper._HYPERLINK_THEME_TAG):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 50])
                dpg.add_theme_color(dpg.mvThemeCol_Text, BuilderHelper.COLOR_TEXT_BLUE)

    @staticmethod
    def deleteHyperlinkTheme() -> None:
        dpg.delete_item("__demo_hyperlinkTheme")

    @staticmethod
    def addHyperlink(text: str, onClick: str | Callable[[], Any]) -> None:
        """
        :param text:
        :param onClick: URL to open (if string) or custom callback (if Callable)
        """
        if isinstance(onClick, str):
            callback = lambda: webbrowser.open(onClick)
        else:
            callback = onClick

        button = dpg.add_button(label=text, callback=callback)
        dpg.bind_item_theme(button, BuilderHelper._HYPERLINK_THEME_TAG)

    @staticmethod
    def padButtonText(text: str, minPadding: int=1, minLength: int=5) -> str:
        missingLength = minLength - len(text)
        paddingLength = math.ceil(missingLength / 2)
        paddingLength = max(paddingLength, minPadding)
        padding = ' ' * paddingLength

        return f'{padding}{text}{padding}'

    @staticmethod
    def addImage(filepath: str, tag : str = 'image') -> None:
        """
        :param filepath:
        :param tag: Tag should be changed if adding more than 1 image in 1 modal
        """

        width, height, channels, data = dpg.load_image(filepath)

        with dpg.texture_registry():
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=data,
                tag=tag,
            )

        dpg.add_image(tag)

    @staticmethod
    def addHelpText(text: str) -> None:
        lastItem = dpg.last_item()

        group = dpg.add_group(horizontal=True)
        dpg.move_item(lastItem, parent=group)

        dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
        textItem = dpg.add_text('(?)', color=[0, 255, 0])

        with dpg.tooltip(textItem):
            dpg.add_text(text)
