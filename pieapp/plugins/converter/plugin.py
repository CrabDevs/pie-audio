from pathlib import Path

from __feature__ import snake_case

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QListWidgetItem

from pieapp.structs.media import MediaFile
from pieapp.structs.plugins import Plugin
from pieapp.structs.layouts import Layout
from pieapp.structs.menus import MainMenu
from pieapp.structs.menus import MainMenuItem
from pieapp.structs.workbench import WorkbenchItem
from piekit.globals import Global
from piekit.helpers.files import create_temp_directory
from piekit.observers.filesystem import FileSystemWatcher
from piekit.plugins import get_plugin

from piekit.widgets.menus import INDEX_START
from piekit.managers.structs import Section
from piekit.plugins.plugins import PiePlugin
from piekit.plugins.mixins import CoreAccessorsMixin
from piekit.plugins.mixins import LayoutAccessorsMixin
from piekit.plugins.decorators import on_plugin_event

from converter.workers import ConverterWorker
from converter.confpage import ConverterConfigPage
from converter.widgets.item import ConverterItem
from converter.widgets.search import ConverterSearch
from converter.widgets.list import ConverterListWidget


class Converter(
    PiePlugin,
    CoreAccessorsMixin,
    LayoutAccessorsMixin
):
    name = Plugin.Converter
    requires = [Plugin.MenuBar, Plugin.Workbench, Plugin.Preferences]
    sig_converter_table_ready = Signal()

    def __init__(self, *args, **kwargs) -> None:
        super(Converter, self).__init__(*args, **kwargs)
        self._watcher = FileSystemWatcher(self)
        self._temp_folder: Path = None
        self._current_files: list[Path] = []
        self._converter_item_widgets: list[ConverterItem] = []

        self._chunk_size = self.get_config(
            key="ffmpeg.chunk_size",
            default=10,
            scope=Section.Root,
            section=Section.User,
        )
        self._ffmpeg_command = Path(
            self.get_config(
                key="ffmpeg.ffmpeg",
                default="ffmpeg",
                scope=Section.Root,
                section=Section.User
            )
        )
        self._ffprobe_command = Path(
            self.get_config(
                key="ffmpeg.ffprobe",
                default="ffprobe",
                scope=Section.Root,
                section=Section.User
            )
        )

    def get_plugin_icon(self) -> "QIcon":
        return self.get_svg_icon("icons/app.svg")

    def get_config_page(self) -> "ConfigPage":
        return ConverterConfigPage()

    def init(self) -> None:
        # Setup grid layouts
        self._list_grid_layout = QGridLayout()
        self._main_layout = self.get_layout(Layout.Main)
        self._main_layout.add_layout(self._list_grid_layout, 1, 0, Qt.AlignmentFlag.AlignTop)

        # Setup search field
        self._search = ConverterSearch()
        self._search.set_hidden(True)
        self._search.textChanged.connect(self._on_search_text_changed)

        # Setup content list
        self._content_list = ConverterListWidget(
            change_callback=self._content_list_item_removed,
            remove_callback=self._content_list_item_removed
        )
        self.add_shortcut("converter-toggle-search", "Ctrl+F", self._toggle_search, self._content_list)

        # Setup placeholder
        self._pixmap_label = QLabel()
        self._pixmap_label.set_pixmap(self.get_icon("icons/package.svg", section=self.name).pixmap(100))
        self._pixmap_label.set_alignment(Qt.AlignmentFlag.AlignCenter)

        self._text_label = QLabel()
        self._text_label.set_text(self.translate("No files selected"))
        self._text_label.set_alignment(Qt.AlignmentFlag.AlignCenter)

        # Setup placeholder
        self._set_placeholder()

    def on_system_shutdown(self) -> None:
        if self._temp_folder:
            if not self._temp_folder.exists():
                return

            for file in self._temp_folder.iterdir():
                file.unlink(missing_ok=True)
            self._temp_folder.rmdir()

    def disable_side_menu_items(self) -> None:
        """
        A proxy method to disable all QuickActionMenu's items
        """
        for item in self._converter_item_widgets:
            item.set_items_disabled()

    # Public proxy methods

    def add_quick_action(
        self,
        name: str,
        text: str,
        icon: QIcon,
        callback: callable = None,
        before: str = None,
        after: str = None,
    ) -> None:
        """
        A proxy method to add an item in the QuickActionMenu
        """
        for item in self._converter_item_widgets:
            item.add_quick_action(name, text, icon, callback, before, after)

    # Public API methods

    def open_files(self) -> None:
        self._temp_folder = create_temp_directory(
            prefix=self.name,
            temp_directory=self.get_config(
                key="ffmpeg.temp_folder",
                default=Global.USER_ROOT / Global.DEFAULT_TEMP_FOLDER_NAME,
                scope=Section.Root,
                section=Section.User
            )
        )

        selected_files = QFileDialog.get_open_file_names(caption=self.translate("Open files"))[0]
        selected_files = list(map(Path, selected_files))
        if not selected_files:
            return

        # chunks = self._split_by_chunks(selected_files[0], self._chunk_size)
        pool = QThreadPool.global_instance()

        for index, selected_file in enumerate(selected_files):
            if selected_file not in self._current_files:
                self._current_files.append(selected_file)
            else:
                del selected_files[index]

        worker = ConverterWorker(
            chunk=selected_files,
            temp_folder=self._temp_folder,
            ffmpeg_cmd=self._ffmpeg_command,
            ffprobe_cmd=self._ffprobe_command,
        )
        worker.signals.started.connect(self._worker_started)
        worker.signals.completed.connect(self._worker_finished)
        pool.start(worker)

    def _worker_started(self) -> None:
        get_plugin(Plugin.StatusBar).show_message(self.translate("Loading files"))

    def _worker_finished(self, models_list: list[MediaFile]) -> None:
        self._fill_list(models_list)
        get_plugin(Plugin.StatusBar).show_message(self.translate("Done loading files"))

    def _fill_list(self, media_files: list[MediaFile]) -> None:
        if not media_files:
            return

        self._clear_placeholder()
        self._list_grid_layout.add_widget(self._search, 0, 0)
        self._list_grid_layout.add_widget(self._content_list, 1, 0)

        for index, media_file in enumerate(media_files):
            widget = ConverterItem(self._content_list, media_file, self.get_theme_property("converterItemColors"))
            widget.set_title(media_file.info.filename)
            widget.set_description(f"{media_file.info.bit_rate}kb/s")
            widget.set_icon(media_file.info.file_format)

            # Add default buttons
            widget.add_quick_action(
                name="delete",
                text=self.translate("Delete"),
                icon=self.get_svg_icon("icons/delete.svg", self.get_theme_property("dangerBackgroundColor")),
                callback=self._delete_tool_button_connect
            )

            widget_layout = QHBoxLayout()
            widget_layout.add_stretch()
            widget_layout.add_widget(widget)

            item = QListWidgetItem()
            item.set_size_hint(widget.size_hint())

            # A really nasty hack to get item `row` inside `QWidgetItem`
            widget.set_list_widget(item)

            self._content_list.add_item(item)
            self._content_list.set_item_widget(item, widget)

            self._converter_item_widgets.append(widget)

        self.get_tool_button(self.name, WorkbenchItem.Clear).set_disabled(False)
        self.sig_converter_table_ready.emit()

    # ConverterListWidget private methods

    def _content_list_item_removed(self) -> None:
        """
        Disable `clear` button on empty `content_list`
        """
        if self._content_list.count() == 0:
            self.get_tool_button(self.name, WorkbenchItem.Clear).set_disabled(True)

    # Private/protected methods

    def _set_placeholder(self) -> None:
        """
        Show placeholder
        """
        self._list_grid_layout.add_widget(self._pixmap_label, 1, 0)
        self._list_grid_layout.add_widget(self._text_label, 2, 0)

    def _clear_placeholder(self) -> None:
        """
        Remove placeholder
        """
        self._list_grid_layout.remove_widget(self._text_label)
        self._list_grid_layout.remove_widget(self._pixmap_label)

    def _clear_content_list(self) -> None:
        """
        Clear content list, remove it from the `list_grid_layout` and disable clear button
        """
        self._converter_item_widgets = []
        self._content_list.clear()

        self._list_grid_layout.remove_widget(self._search)
        self._list_grid_layout.remove_widget(self._content_list)
        self._set_placeholder()

        self._current_files = []
        self.get_tool_button(self.name, WorkbenchItem.Clear).set_disabled(True)

    def _delete_tool_button_connect(self, _: MediaFile) -> None:
        selected_index = self._content_list.selected_indexes()[0]
        self._content_list.take_item(selected_index.row())
        del self._converter_item_widgets[selected_index.row()]

    # ConverterSearch private methods

    def _toggle_search(self) -> None:
        self._search.set_hidden(not self._search.is_hidden())
        self._search.set_focus()

    @Slot(str)
    def _on_search_text_changed(self, text: str) -> None:
        """
        Filter `content_list` by text
        """
        for row in range(self._content_list.count()):
            item = self._content_list.item(row)
            widget = self._content_list.item_widget(item)
            if text:
                item.set_hidden(not (text.lower() in widget.media_file.info.filename.lower()))
            else:
                item.set_hidden(False)

    # Plugin event method

    @on_plugin_event(target=Plugin.Preferences)
    def _on_preferences_available(self) -> None:
        preferences = get_plugin(Plugin.Preferences)
        preferences.register_config_page(self)

    @on_plugin_event(target=Plugin.Preferences, event="on_teardown")
    def _on_preferences_teardown(self) -> None:
        preferences = get_plugin(Plugin.Preferences)
        preferences.deregister_config_page(self)

    @on_plugin_event(target=Plugin.MenuBar)
    def _on_menu_bar_available(self) -> None:
        """
        Add open file element in the "File" menu
        """
        self.add_menu_item(
            section=Section.Shared,
            menu=MainMenu.File,
            name=MainMenuItem.OpenFiles,
            text=self.translate("Open file"),
            icon=self.get_svg_icon("icons/folder-open.svg"),
            index=INDEX_START(),
            triggered=self.open_files
        )

    @on_plugin_event(target=Plugin.Workbench)
    def _on_workbench_available(self) -> None:
        """
        Add tool button on the `Workbench`
        """
        self.add_tool_button(
            section=self.name,
            name=WorkbenchItem.OpenFiles,
            text=self.translate("Open file"),
            tooltip=self.translate("Open file"),
            icon=self.get_svg_icon("icons/folder.svg"),
            triggered=self.open_files
        )

        self.add_tool_button(
            section=self.name,
            name=WorkbenchItem.Convert,
            text=self.translate("Convert"),
            tooltip=self.translate("Convert"),
            icon=self.get_svg_icon("icons/bolt.svg")
        ).set_enabled(False)

        clear_tool_button = self.add_tool_button(
            section=self.name,
            name=WorkbenchItem.Clear,
            text=self.translate("Clear"),
            tooltip=self.translate("Clear"),
            icon=self.get_svg_icon("icons/delete.svg")
        )
        clear_tool_button.set_enabled(False)
        clear_tool_button.clicked.connect(self._clear_content_list)

        self.add_toolbar_item(
            toolbar=Plugin.Workbench,
            name=WorkbenchItem.OpenFiles,
            item=self.get_tool_button(self.name, WorkbenchItem.OpenFiles),
        )

        self.add_toolbar_item(
            toolbar=Plugin.Workbench,
            name=WorkbenchItem.Convert,
            item=self.get_tool_button(self.name, WorkbenchItem.Convert),
            after=WorkbenchItem.OpenFiles
        )

        self.add_toolbar_item(
            toolbar=Plugin.Workbench,
            name=WorkbenchItem.Clear,
            item=self.get_tool_button(self.name, WorkbenchItem.Clear),
            after=WorkbenchItem.Convert
        )


def main(parent: "QMainWindow", plugin_path: "Path"):
    return Converter(parent, plugin_path)
