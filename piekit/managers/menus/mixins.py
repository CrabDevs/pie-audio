from typing import Union

from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QWidget

from piekit.widgets.menus import PieMenu, INDEX_END, INDEX_START
from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager, Section


class MenuAccessorMixin:

    def add_menu_bar(
        self,
        parent: "QObject",
        name: str = None
    ) -> QMenuBar:
        menu_bar = QMenuBar(parent)
        return Managers(SysManager.Menus).add_item(name, menu_bar)

    def get_menu_bar(self, name: str) -> QMenuBar:
        return Managers(SysManager.Menus).get_item(name)

    def add_menu(
        self,
        parent: QMenuBar = None,
        section: str = None,
        name: str = None,
        text: str = None,
        icon: QIcon = None,
    ) -> PieMenu:
        menu = PieMenu(parent=parent, name=name, text=text)
        if icon:
            menu.menu_action().set_icon_visible_in_menu(True)
            menu.set_icon(icon)

        return Managers(SysManager.Menus).add_item(name, menu, section or Section.Shared)

    def add_menu_item(
        self,
        section: str = None,
        menu: str = None,
        name: str = None,
        text: str = None,
        triggered: callable = None,
        icon: QIcon = None,
        before: str = None,
        index: Union[int, INDEX_START, INDEX_END] = None
    ) -> QAction:
        manager = Managers(SysManager.Menus)
        menu_instance = manager.get_item(menu, section)
        menu_instance.add_menu_item(name, text, triggered, icon, before, index)
        return manager.add_item(name, menu_instance, menu)

    def get_menu(self, section: str, name: str) -> PieMenu:
        return Managers(SysManager.Menus).get_menu(section or Section.Shared, name)

    def get_menu_item(self, menu: str, name: str) -> QAction:
        return Managers(SysManager.Menus).get_menu_item(name, menu)

    addMenu = add_menu
    getMenu = get_menu
    addMenuBar = add_menu_bar
    getMenuBar = get_menu_bar
    getMenuItem = get_menu_item
    addMenuItem = add_menu_item
