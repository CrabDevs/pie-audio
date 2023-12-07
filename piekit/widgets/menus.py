from __future__ import annotations
from __feature__ import snake_case

from typing import Union, Any

from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMenu

from piekit.exceptions import PieException
from piekit.widgets.actions import PieAction


INDEX_END = type("INDEX_END", (), {})
INDEX_START = type("INDEX_START", (), {})


class PieMenu(QMenu):

    def __init__(
        self,
        parent: QMenuBar = None,
        name: str = None,
        text: str = None,
    ) -> None:
        self._name = name
        self._text = text

        self._actions_list: list = []
        self._actions_dict: dict[str, QAction] = {}

        if text is not None:
            super().__init__(parent=parent, title=text)
        else:
            super().__init__(parent=parent)

    def add_item(
        self,
        action: PieAction,
        before: str = None,
        after: str = None
    ) -> PieAction:
        self._actions_dict[action.action_id] = action
        self._actions_list.append(action)

        if isinstance(index, INDEX_START):
            index = self._actions_dict[self._actions_list[0]]
            self.insert_action(index, action)

        elif isinstance(index, INDEX_END):
            index = self._actions_dict[self._actions_list[-1]]
            self.insert_action(index, action)

        elif isinstance(index, int):
            index = self._actions_dict[self._actions_list[index]]
            self.insert_action(index, action)

        elif before:
            before = self._actions_dict[before]
            self.insert_action(before, action)

        else:
            self.add_action(action)

        return action

    def get_item(self, name: str) -> QAction:
        return self._actions_dict[name]

    def get_items(self) -> list[QAction]:
        return self._actions_list

    @property
    def name(self) -> str:
        return self._name
