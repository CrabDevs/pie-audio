from typing import Any, Union

from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager, Scope


class ConfigAccessorMixin:
    """
    Config mixin made for PiePlugin based plugins/containers
    """

    def get_config(
        self,
        key: Any,
        default: Any = None,
        temp: bool = False,
        scope: Union[str, Scope.Root] = None,
        section: Union[Scope.Inner, Scope.User] = Scope.Inner,
    ) -> Any:
        return Managers(SysManager.Configs).get(scope or self.name, section, key, default, temp=temp)

    def set_config(
        self,
        key: Any,
        data: Any,
        temp: bool = False,
        scope: Union[str, Scope.Root] = None,
        section: Union[Scope.Inner, Scope.User] = Scope.Inner,
    ) -> None:
        Managers(SysManager.Configs).set(scope or self.name, section, key, data, temp=temp)

    def delete_config(
        self,
        key: Any,
        scope: Union[str, Scope.Root] = None,
        section: Union[Scope.Inner, Scope.User] = Scope.Inner,
    ) -> None:
        Managers(SysManager.Configs).delete(scope or self.name, section, key)

    def save_config(
        self,
        scope: Union[str, Scope.Root] = None,
        section: Union[Scope.Inner, Scope.User] = Scope.Inner,
        temp: bool = False,
        create: bool = False
    ) -> None:
        Managers(SysManager.Configs).save(scope or self.name, section, temp=temp, create=create)

    def restore_config(
        self,
        key: Any = None,
        scope: Union[str, Scope.Root] = None,
        section: Union[Scope.Inner, Scope.User] = Scope.Inner,
    ) -> None:
        Managers(SysManager.Configs).restore(scope or self.name, section, key)

    getConfig = get_config
    setConfig = set_config
    saveConfig = save_config
    deleteConfig = delete_config
    restoreConfig = restore_config
