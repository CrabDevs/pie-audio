from piekit.config.types import Lock
from piekit.managers.structs import DirectoryType
from piekit.managers.structs import ManagerConfig


PIEAPP_NAME: Lock = "pie-audio"
PIEAPP_VERSION: Lock = "2023.04.pre-alpha"
# List of excluded file formats
ASSETS_EXCLUDED_FORMATS = [DirectoryType, ".qss", ".json", ".ttf", ".py"]

# Managers startup configuration
# TODO: Replace `init` attribute with Qt signal name (str) and emit it via `QMetaObject` -> `invokeMethod`
INITIAL_MANAGERS: Lock = [
    ManagerConfig(
        import_string="piekit.managers.configs.manager.ConfigManager",
        init=True
    ),
    ManagerConfig(
        import_string="piekit.managers.locales.manager.LocaleManager",
        init=True
    ),
    ManagerConfig(
        import_string="piekit.managers.assets.manager.AssetsManager",
        init=True
    ),
]

MANAGERS: Lock = [
    *INITIAL_MANAGERS,
    ManagerConfig(
        import_string="piekit.managers.plugins.manager.PluginManager",
        init=False
    ),
    ManagerConfig(
        import_string="piekit.managers.menus.manager.MenuManager",
        init=True
    ),
    ManagerConfig(
        import_string="piekit.managers.toolbars.manager.ToolBarManager",
        init=True
    ),
    ManagerConfig(
        import_string="piekit.managers.toolbuttons.manager.ToolButtonManager",
        init=True
    )
]
