import math
import webbrowser

import dearpygui.dearpygui as dpg


class BuilderHelper:
    _hyperlinkThemeTag = '_app_hyperlink_theme'

    @staticmethod
    def registerHyperlinkTheme() -> None:
        """
        Hyperlink code from dpg demo.py
        """
        dpg.add_texture_registry(label='_app_texture_container', tag='_app_texture_container')

        with dpg.theme(tag=BuilderHelper._hyperlinkThemeTag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 50])
                dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])

    @staticmethod
    def deleteHyperlinkTheme() -> None:
        dpg.delete_item("__demo_hyperlinkTheme")

    @staticmethod
    def addHyperlink(text: str, address: str) -> None:
        button = dpg.add_button(label=text, callback=lambda: webbrowser.open(address))
        dpg.bind_item_theme(button, BuilderHelper._hyperlinkThemeTag)

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
