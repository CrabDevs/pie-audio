from typing import Union

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QToolButton

from piekit.widgets.menus import PieMenu
from piekit.widgets.menus import INDEX_END
from piekit.widgets.menus import INDEX_START
from piekit.widgets.actions import PieAction

from piekit.exceptions import PieException
from piekit.managers.structs import Section
from piekit.managers.structs import SysManager
from piekit.managers.registry import Managers


class MenuAccessorMixin:

    def add_menu(self, name: str, text: str, icon: QIcon = None) -> None:
        """
        This proxy method adds and registers `PieMenu` into `MenuManager` registry.

        Args:
            name (str): Menu name
            text (str): Text to display
            icon (QIcon): QIcon object instance
        """
        menu_instance = PieMenu(parent=self, name=name, text=text)
        if icon is not None:
            menu_instance.menu_action().set_icon_visible_in_menu(True)
            menu_instance.set_icon(icon)

        Managers(SysManager.Menus).add_item(f"{self.get_class_name()}.{name}", menu_instance)
        return menu_instance

    def add_submenu(
        self,
        parent_menu_name: str,
        submenu_name: str,
        submenu_text: str,
        submenu_icon: QIcon,
        triggered: callable = None,
        before: str = None,
        after: str = None,
    ) -> PieMenu:
        """
        This proxy method adds and registers submenu for parent menu.

        Args:
            parent_menu_name (str): Parent menu name
            submenu_name (str): Submenu name
            submenu_text (str): Submenu text
            submenu_icon (QIcon): QIcon object instance
            triggered (callable): Function to call
            before (str): Name of the element before which you want to place the element
            after (str): Name of the element after which you want to place the element

        Returns:
            PieMenu object instance
        """
        parent_menu_instance = Managers(SysManager.Menus).get_item(parent_menu_name)
        if not parent_menu_instance:
            raise PieException(f"Menu \"{submenu_name}\" not found")

        submenu_instance = PieMenu(parent=self, name=submenu_name, text=submenu_text)
        if submenu_icon is not None:
            parent_menu_instance.menu_action().set_icon_visible_in_menu(True)
            parent_menu_instance.set_icon(submenu_icon)

        if triggered:
            parent_menu_instance.triggered.connect(triggered)

        parent_menu_instance.add_submenu(
            submenu=submenu_instance,
            triggered=triggered, 
            before=before, 
            after=after
        )
        return parent_menu_instance

    def add_menu_item(
        self,
        menu_name: str,
        item_name: str,
        item_object: Union[QToolButton, PieAction],
        before: str = None,
        after: str = None
    ) -> PieAction:
        """
        This proxy method adds item in menu.

        Args:
            menu_name (str): Menu name
            item_name (str): Item name
            item_object (PieAction): Item object instance
            before (str): Name of the element before which you want to place the element
            after (str): Name of the element after which you want to place the element
        
        Returns:
            PieAction object instance
        """
        menu_instance = self.get_menu(menu_name)
        if not menu_instance:
            raise PieException(f"Can't find \"{menu_name}\"")

        if self.get_menu_item(menu_name, item_name):
            raise PieException(f"Item \"{item_name}\" is already exists")

        menu_instance.add_item(item_object, before, after)
        return item_object

    def get_menu_item(self, menu_name: str, item_name: str) -> PieAction:
        """
        This proxy method returns single menu item object instance.

        Args:
            menu_name (str): Menu name
            item_name (str): PieAction item name
        """
        menu_instance = Managers(SysManager.Menus).get_item(f"{self.get_class_name()}.{menu_name}")
        if not menu_instance:
            raise PieException(f"Menu \"{menu_name}\" not found")

        item_instance = menu_instance.get_item(item_name)
        if not item_instance:
            raise PieException(f"Item \"\{item_name}\" not found")

        return item_instance

    def get_menu_items(self, menu_name: str) -> list[PieAction]:
        """
        This proxy method returns list of `PieAction` object instances.

        Args:
            menu_name (str): Menu name

        Returns:
            list of `PieAction` object instances
        """
        menu_instance = Managers(SysManager.Menus).get_item(f"{self.get_class_name()}.{menu_name}")
        if not menu_instance:
            raise PieException(f"Menu \"{menu_name}\" not found")

        return menu_instance.get_items()

    def get_menu(self, menu_name: str) -> PieMenu:
        """
        This proxy method returns `PieMenu` object instance by its name.

        Args:
            menu_name (str): Menu name

        Returns:
            PieMenu object instance
        """
        return Managers(SysManager.Menus).get_item(f"{self.get_class_name()}.{menu_name}")

    def get_menus(self, *names: str, parent_key: str = None) -> dict[str, PieMenu]:
        return Managers(SysManager.Menus).get_items(names, parent_key)


class MenuAccessorMixin:

    def add_menu_bar(
        self,
        parent: QWidget = None,
        name: str = None
    ) -> QMenuBar:
        menu_bar = QMenuBar(parent)
        return Managers(SysManager.Menus).add_menu_bar(name or Section.Shared, menu_bar)

    def get_menu_bar(self, name: str) -> QMenuBar:
        return Managers(SysManager.Menus).get_menu_bar(name or Section.Shared)

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

        return Managers(SysManager.Menus).add_menu(section or Section.Shared, name, menu)

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
    ) -> PieAction:
        manager = Managers(SysManager.Menus)
        menu_instance = manager.get_menu(section, menu)
        menu_instance.add_menu_item(name, text, triggered, icon, before, index)
        return manager.add_menu_item(section or Section.Shared, menu, name, menu_instance)

    def get_menu(self, section: str, name: str) -> PieMenu:
        return Managers(SysManager.Menus).get_menu(section or Section.Shared, name)

    def get_menu_item(self, section: str, menu: str, name: str) -> PieAction:
        return Managers(SysManager.Menus).get_menu_item(section, menu, name)

    addMenu = add_menu
    getMenu = get_menu
    addMenuBar = add_menu_bar
    getMenuBar = get_menu_bar
    getMenuItem = get_menu_item
    addMenuItem = add_menu_item
