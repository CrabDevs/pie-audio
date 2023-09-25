from __feature__ import snake_case

from typing import Union

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QObject, QSize
from PySide6.QtWidgets import QToolButton

from piekit.globals import Global
from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager, Section


class ToolButtonAccessorMixin:

    def add_tool_button(
        self,
        parent: QObject = None,
        section: Union[str, Section] = Section.Shared,
        name: str = None,
        text: str = None,
        tooltip: str = None,
        icon: QIcon = None,
        triggered: callable = None,
        only_icon: bool = False,
        object_name: str = None,
        text_position: Qt.ToolButtonStyle = Qt.ToolButtonStyle.ToolButtonTextUnderIcon
    ) -> QToolButton:
        tool_button = QToolButton(parent=parent)
        if icon:
            tool_button.set_icon(icon)

        if tooltip:
            tool_button.set_tool_tip(tooltip)

        if text:
            tool_button.set_text(text)

        if triggered:
            tool_button.clicked.connect(triggered)

        if object_name:
            tool_button.set_object_name(object_name)

        if only_icon:
            tool_button.set_tool_button_style(Qt.ToolButtonStyle.ToolButtonIconOnly)
        else:
            tool_button.set_tool_button_style(text_position)

        tool_button.set_focus_policy(Qt.FocusPolicy.NoFocus)
        tool_button.set_icon_size(QSize(*Global.TOOL_BUTTON_ICON_SIZE))

        return Managers(SysManager.ToolButtons).add_item(name, tool_button, parent_name=section or Section.Shared)

    def get_tool_buttons(self, *names: str, section: str) -> list[QObject]:
        return Managers(SysManager.ToolButtons).get_items(*names, parent_name=section or Section.Shared)

    def get_tool_button(self, section: str, name: str) -> QToolButton:
        return Managers(SysManager.ToolButtons).get_item(name, section or Section.Shared)

    addToolButton = add_tool_button
    getToolButton = get_tool_button
    getToolButtons = get_tool_buttons
