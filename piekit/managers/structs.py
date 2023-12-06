"""
Default managers
"""


class SysManager:
    # ConfigManager
    Configs = "configs"
    
    # LocaleManager
    Locales = "locales"
    
    # AssetsManager
    Themes = "assets"

    # ShortcutsManager
    Shortcuts = "shortcuts"

    # PluginManager
    Plugins = "plugins"
    
    # MenuManager
    Menus = "menus"

    # ToolButtonManager
    ToolButton = "toolbuttons"

    # ToolBarManager
    ToolBars = "toolbar"

    # ActionManager
    Actions = "actions"

    # ConfigPageManager
    ConfigPages = "configpages"

    # LayoutManager
    Layouts = "layouts"
    

class Scope:
    """
    This structure is designed to separate scopes in registries.
    """

    # Root/application scope
    Root = "root"
    
    # Plugin scope
    Inner = "inner"

    # User scope
    User = "user"
    
    # Shared scope
    Shared = "shared"


AllPlugins = "__ALL__"
