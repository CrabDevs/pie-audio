from __future__ import annotations

from typing import Union

from PySide6.QtGui import QAction

from piekit.managers.structs import SysManager
from piekit.managers.managers import ReferenceManagerMixin


ActionManager = ReferenceManagerMixin(SysManager.Actions)
