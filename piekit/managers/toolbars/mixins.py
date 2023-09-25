from typing import Union

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager, Section
from piekit.widgets.toolbars import PieToolBar


class ToolBarAccessorMixin:

    def add_toolbar(
        self,
        parent: QObject = None,
        name: str = None
    ) -> PieToolBar:
        toolbar = PieToolBar(parent=parent, name=name)
        return Managers(SysManager.ToolBars).add_item(name or Section.Shared, toolbar)

    def add_toolbar_item(
        self,
        section: str = None,
        name: str = None,
        item: Union[QWidget, QAction] = None,
        after: str = None,
        before: str = None
    ) -> Union[QAction, QWidget]:
        manager = Managers(SysManager.ToolBars)
        toolbar: PieToolBar = manager.get_toolbar(section)
        toolbar.add_toolbar_item(name, item, after, before)
        return manager.add_item(name, item, section or Section.Shared)

    def get_toolbar_item(self, section: str, name: str) -> QWidget:
        return Managers(SysManager.ToolBars).get_item(name, section)

    def get_toolbar_items(self, section: str, *names: str) -> list[QObject]:
        return Managers(SysManager.ToolBars).get_items(*names, parent_name=section)

    def get_toolbar(self, name: str) -> PieToolBar:
        return Managers(SysManager.ToolBars).get_item(name)

    def get_toolbars(self, *names: str) -> list[PieToolBar]:
        return Managers(SysManager.ToolBars).get_items(*names)

    addToolBar = add_toolbar
    getToolBar = get_toolbar
    getToolBars = get_toolbars
    addToolBarItem = add_toolbar_item
    getToolBarItem = get_toolbar_item
    getToolBarItems = get_toolbar_items
