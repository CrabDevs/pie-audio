from __feature__ import snake_case

from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QLabel, QGridLayout, QPushButton, QDialog

from pieapp.structs.menus import MainMenu
from piekit.managers.structs import Scope
from piekit.plugins.plugins import PiePlugin
from pieapp.structs.plugins import Plugin
from piekit.managers.menus.mixins import MenuAccessorMixin

from piekit.globals import Global
from piekit.managers.themes.mixins import ThemeAccessorMixin
from piekit.managers.locales.mixins import LocalesAccessorMixin
from piekit.managers.plugins.decorators import on_plugin_event


class About(
    PiePlugin,
    MenuAccessorMixin,
    LocalesAccessorMixin,
    ThemeAccessorMixin,
):
    name = Plugin.About
    requires = [Plugin.MenuBar]

    def call(self) -> None:
        self._dialog = QDialog(self._parent)
        self._dialog.set_modal(True)
        self._dialog.set_window_title(self.translate("About"))
        self._dialog.set_window_icon(self.get_plugin_icon())
        self._dialog.resize(400, 300)

        ok_button = QPushButton(self.translate("Ok"))
        ok_button.clicked.connect(self._dialog.close)

        pixmap = QPixmap()
        pixmap.load(self.get_file_path("icons/app.svg"))

        icon_label = QLabel()
        icon_label.set_pixmap(pixmap)

        description_label = QLabel()
        description_label.set_text(
            f'{self.translate("Pie Audio • Simple Audio Editor")} '
            f'({Global.PIEAPP_APPLICATION_VERSION})'
        )

        github_link_label = QLabel()
        github_link_label.set_open_external_links(True)
        github_link_label.set_text(f"<a href='{Global.PIEAPP_PROJECT_URL}'>{self.translate('Project URL')}</a>")

        grid_layout = QGridLayout()
        grid_layout.add_widget(icon_label, 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        grid_layout.add_widget(description_label, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        grid_layout.add_widget(github_link_label, 2, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        grid_layout.add_widget(ok_button, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)

        self._dialog.set_layout(grid_layout)
        self._dialog.show()

    @on_plugin_event(target=Plugin.MenuBar)
    def on_menu_bar_available(self) -> None:
        self.add_menu_item(
            section=Scope.Shared,
            menu=MainMenu.Help,
            name="about",
            text=self.translate("About"),
            triggered=self.call,
            icon=self.get_svg_icon("icons/help.svg"),
        )

    def get_plugin_icon(self) -> "QIcon":
        return self.get_svg_icon("icons/app.svg", section=self.name)


def main(parent: "QMainWindow", plugin_path: "Path") -> Union[PiePlugin, None]:
    return About(parent, plugin_path)
