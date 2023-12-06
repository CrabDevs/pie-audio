from typing import Any
from piekit.exceptions import PieException


class BaseManager:
    """
    Base manager class
    """
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
        return f'({self.__class__.__name__}) <name: {self.name}>'


class BaseRegistry:
    """
    Base registry class. 
    Simillar to the `BaseManager` it's designed to reduce codebase
    """
    name: str

    def __init__(self, container_type: dict = None) -> None:
        """
        Args:
            name (str): Registry class name
            container_type (dict): Dict or dict based container type
        """
        # All data stores in `container` with the next signature:
        # `<parent key>.<key>`: {<data>} or `<key>`: {<data>}
        self._container: dict[str, dict[str, Any]] = container_type({})

    def init(self, *args, **kwargs) -> None:
        """
        This method is used to initialize all containers, variables, etc.
        Define variables in the `__init__` method
        """

    def shutdown(self, *args, **kwargs):
        """
        This method is used to reset all containers, variables, etc. without removing them from memory
        """
        self._container.clear()

    def reload(self):
        self.shutdown()
        self.init()

    def add_item(
        self,
        name: str,
        item: Any = None,
        parent_name: str = None,
    ) -> Any:
        if name and parent_name:
            key_path = f"{parent_name}.{name}"
            if key_path not in self._container:
                self._container[key_path] = item
                return item
            else:
                raise PieException(f"Item \"{name}\" is already added in \"{parent_name}\"")

        if name not in self._container:
            self._container[name] = item
            return item

        raise PieException(f"Item \"{name}\" is already added")

    def get_item(
        self,
        name: str,
        parent_name: str
    ) -> Any:
        if name and parent_name:
            key_path = f"{parent_name}.{name}"
            if key_path in self._container:
                return self._container[key_path]
            else:
                raise PieException(f"Item \"{name}\" was not found in \"{parent_name}\"")

        if name in self._container:
            return self._container[name]

        raise PieException(f"Item \"{name}\" doesn't exists")

    def get_items(self, *names: str, parent_name: str = None) -> list[Any]:
        if parent_name and self._container.get(parent_name):
            parent_items = self._container[parent_name]
            return [parent_items.get(n) for n in names if n in parent_items]
        elif not parent_name:
            return [self._container.get(n) for n in names if n in self._container]
        else:
            return []

    def delete_item(
        self,
        name: str,
        parent_name: str
    ) -> Any:
        if name and parent_name:
            key_path = f"{parent_name}.{name}"
            if key_path in self._container:
                del self._container[key_path]
            else:
                raise PieException(f"Item \"{name}\" was not found in \"{parent_name}\"")

        if name in self._container:
            del self._container[name]

        raise PieException(f"Item \"{name}\" doesn't exists")
    
    def __repr__(self) -> str:
        return f"({self.__class__.__name__}) <name: {self.name}>"
