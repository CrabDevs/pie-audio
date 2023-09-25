"""
Base manager
"""
from pathlib import Path
from typing import Any
from PySide6.QtCore import QObject

from piekit.exceptions import PieException
from piekit.managers.registry import Managers


class BaseManager:
    # Manager name
    name: str

    def init(self, *args, **kwargs) -> None:
        """
        Optional initializer
        """

    def shutdown(self, *args, **kwargs):
        """
        This method serves to reset all containers, variables etc.
        Don't use it to delete data from memory
        """

    def reload(self):
        """
        This method reload manager
        """
        self.shutdown()
        self.init()

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f'({self.__class__.__name__}) <id: {id(self)}>'


class PluginBaseManager(BaseManager):

    def init_plugin(self, plugin_folder: Path) -> None:
        raise NotImplementedError(f"Method `init_plugin` must be implemented")

    def on_post_init_plugin(self, plugin_folder: Path) -> None:
        pass

    def shutdown_plugin(self) -> None:
        pass

    def on_post_shutdown(self) -> None:
        pass


class ReferenceManager(BaseManager):

    def __init__(
        self,
        manager_name: str,
        dict_type: dict = None
    ) -> None:
        """
        Args:
            manager_name (str): name of the manager
            dict_type (dict): dict or dict based structure
        """
        super().__init__()
        
        if Managers(manager_name):
            raise PieException(f"Manager \"{manager_name}\" is already registered")

        self.name = manager_name
        self._registry: dict[str, dict[str, Any]] = dict_type({}) if dict_type else {}

    def shutdown(self, *args, **kwargs):
        self._registry.clear()

    def add_item(
        self,
        name: str,
        item: QObject = None,
        parent_name: str = None,
    ) -> QObject:
        if name and parent_name:
            key_path = f"{parent_name}.{name}"
            if key_path not in self._registry:
                self._registry[key_path] = item
                return item
            else:
                raise PieException(f"Item \"{name}\" is already added in \"{parent_name}\"")

        if name not in self._registry:
            self._registry[name] = item
            return item

        raise PieException(f"Item \"{name}\" is already added")

    def get_item(
        self,
        name: str,
        parent_name: str
    ) -> QObject:
        if name and parent_name:
            key_path = f"{parent_name}.{name}"
            if key_path in self._registry:
                return self._registry[key_path]
            else:
                raise PieException(f"Item \"{name}\" was not found in \"{parent_name}\"")

        if name in self._registry:
            return self._registry[name]

        raise PieException(f"Item \"{name}\" doesn't exists")

    def get_items(self, *names: str, parent_name: str = None) -> list[QObject]:
        if parent_name and self._registry.get(parent_name):
            parent_items = self._registry[parent_name]
            return [parent_items.get(n) for n in names if n in parent_items]
        elif not parent_name:
            return [self._registry.get(n) for n in names if n in self._registry]
        else:
            return []

    def delete_item(
        self,
        name: str,
        parent_name: str
    ) -> QObject:
        if name and parent_name:
            key_path = f"{parent_name}.{name}"
            if key_path in self._registry:
                del self._registry[key_path]
            else:
                raise PieException(f"Item \"{name}\" was not found in \"{parent_name}\"")

        if name in self._registry:
            del self._registry[name]

        raise PieException(f"Item \"{name}\" doesn't exists")
    
    def __repr__(self) -> str:
        return f"({self.__class__.__name__}) <name: {self.name}>"
