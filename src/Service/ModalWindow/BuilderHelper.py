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
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
                dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])

    @staticmethod
    def deleteHyperlinkTheme() -> None:
        dpg.delete_item("__demo_hyperlinkTheme")

    @staticmethod
    def hyperlink(text: str, address: str) -> None:
        button = dpg.add_button(label=text, callback=lambda: webbrowser.open(address))
        dpg.bind_item_theme(button, BuilderHelper._hyperlinkThemeTag)