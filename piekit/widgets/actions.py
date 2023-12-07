from __feature__ import snake_case

import sys

from PySide6.QtWidgets import QAction


class PieAction(QAction):
    
    def __init__(self, *args, action_id: str = None, **kwargs) -> None:
        super(QAction, self).__init__(*args, **kwargs)
        self._action_id = action_id
        
        if sys.platform == "darwin":
            self.set_icon_visible_in_menu(True)

    @property
    def action_id(self) -> str:
        return self._action_id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> (id: {id(self)} action_id: {self._action_id})"

