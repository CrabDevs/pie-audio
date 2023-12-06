import functools
from typing import Union

from piekit.managers.structs import Scope, Scope
from piekit.exceptions import PieException


def on_configuration_update(
    func: callable = None,
    scope: str = Scope.Root,
    section: str = Scope.Inner,
    key: str = None,
) -> callable:
    pass
