from typing import Any
from typing import Union
from typing import Mapping
from typing import MutableMapping

from dotty_dict import Dotty

from piekit.exceptions import PieException


class BaseManager:
    """
    This class provides single-responsability 
    and is used to manage and store any kind of data
    """
    name: str

    def init(self) -> None:
        """
        Optional initializer
        """

    def shutdown(self):
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
        return f"({self.__class__.__name__}) <id: {id(self)} name: {self.name}>"


class BaseRegistryManager:
    """
    Base registry class. 
    Simillar to the `BaseManager` it's designed to reduce codebase
    """
    name: str
    container_type: Union[Mapping, MutableMapping] = Dotty

    def __init__(self) -> None:
        """
        Args:
            name (str): Registry class name
            container_type (dict): Dict or dict based container type
        """
        # All data stores in `container` with the next signature:
        # `<parent key>.<key>`: {<data>} or `<key>`: {<data>}
        self._container: dict[str, dict[str, Any]] = self.container_type()

    def init(self) -> None:
        """
        This method is used to initialize all containers, variables, etc.
        Define variables in the `__init__` method, if necessary.
        """

    def shutdown(self):
        """
        This method is used to reset all containers, variables, etc. without removing them from memory
        """
        self._container.clear()

    def reload(self):
        self.shutdown()
        self.init()

    def add_item(self, key: str, item: Any = None, parent_key: str = None) -> Any:
        # Handle "parent-children key" case
        if key and parent_key:
            key_path = f"{parent_key}.{key}"
            if key_path not in self._container:
                self._container[key_path] = item
                return item
            else:
                raise PieException(f"Item \"{key}\" is already added in \"{parent_key}\"")

        # Handle "single key" case
        if key not in self._container:
            self._container[key] = item
            return item

        raise PieException(f"Item \"{key}\" in \"{self.name}\" is already added")

    def get_item(self, key: str, parent_key: str) -> Any:
        # Handle "parent-children key" case
        if key and parent_key:
            key_path = f"{parent_key}.{key}"
            if key_path in self._container:
                return self._container[key_path]
            else:
                raise PieException(f"Item \"{key}\" was not found in \"{parent_key}\"")

        # Handle "single key" case
        if key in self._container:
            return self._container[key]

        raise PieException(f"Item \"{key}\" in \"{self.name}\" doesn't exists")

    def get_items(self, *keys: str, parent_key: str = None) -> list[Any]:
        if parent_key and self._container.get(parent_key):
            parent_items = self._container[parent_key]
            return [parent_items.get(n) for n in keys if n in parent_items]
        elif not parent_key:
            return [self._container.get(n) for n in keys if n in self._container]
        else:
            return []

    def delete_item(self, key: str, parent_key: str) -> Any:
        if key and parent_key:
            key_path = f"{parent_key}.{key}"
            if key_path in self._container:
                del self._container[key_path]
            else:
                raise PieException(f"Item \"{key}\" in \"{self.name}\" was not found in \"{parent_key}\"")

        if key in self._container:
            del self._container[key]

        raise PieException(f"Item \"{key}\" in \"{self.name}\" doesn't exists")
    
    def __repr__(self) -> str:
        return f"({self.__class__.__name__}) <id: {id(self)} name: {self.name}>"
