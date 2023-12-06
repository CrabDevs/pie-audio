from typing import Any, Union

from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager, Scope


class LocalesAccessorMixin:
    """
    ConfigManager accessor mixin
    """

    def translate(
        self,
        key: Any,
        section: Union[str, Scope] = Scope.Shared
    ) -> Any:
        return Managers(SysManager.Locales).get(section or self.section, key)

    getTranslation = translate
