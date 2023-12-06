from piekit.managers.structs import Scope
from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager


def translate(text: str, section: Scope.Shared = Scope.Shared) -> str:
    return Managers(SysManager.Locales).get(section, text)
