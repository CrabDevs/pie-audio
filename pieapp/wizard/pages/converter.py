from __feature__ import snake_case

import os
from pathlib import Path

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, QSize, Slot, QDir
from PySide6.QtGui import Qt, QAction
from PySide6.QtWidgets import QStyle, QFileDialog

from pieapp.helpers.ffmpeg import DownloadWorker
from pieapp.api.globals import Global
from pieapp.helpers.logger import logger
from pieapp.api.managers.configs.mixins import ConfigAccessorMixin
from pieapp.api.managers.locales.helpers import translate
from pieapp.api.managers.structs import Section


class ConverterWizardPage(
    ConfigAccessorMixin,
    QtWidgets.QWizardPage
):
    section = Section.Shared

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._ffmpeg_path: Path = Path(Global.USER_ROOT / "ffmpeg")
        file_extension = ".exe" if os.name == "nt" else ""
        self._binaries = tuple(map(lambda v: Path(f"{v}{file_extension}"), ("ffmpeg", "ffprobe", "ffplay")))

        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.set_style_sheet("QProgressBar{font-size: 15pt;}")
        self._progress_bar.set_format(f"{translate('Downloading files...')} (%p%/100%)")
        self._progress_bar.set_alignment(Qt.AlignmentFlag.AlignCenter)

        self._download_thread = QThread()
        self._download_worker = DownloadWorker()
        self._download_worker.sig_download_progress.connect(self._show_downloader_progress)
        self._download_worker.sig_download_done.connect(self._show_downloader_ready)
        self._download_worker.sig_unpack_archive_message.connect(self._download_worker_unpack)
        self._download_worker.sig_unpack_ready.connect(self._unpack_ready)
        self._download_worker.move_to_thread(self._download_thread)
        self._download_thread.started.connect(self._download_worker.start)
        self._download_thread.finished.connect(self._download_worker.delete_later)
        self._download_worker.destroyed.connect(self._download_worker.destroyed)

        self.line_edit_action = QAction()
        self.line_edit_action.set_icon(self.style().standard_icon(QStyle.StandardPixmap.SP_DirIcon))
        self.line_edit_action.triggered.connect(self.select_ffmpeg_root_path)

        self._download_button = QtWidgets.QPushButton()
        self._download_button.set_icon(self.style().standard_icon(QStyle.StandardPixmap.SP_ArrowDown))
        self._download_button.set_icon_size(QSize(27, 27))
        self._download_button.clicked.connect(self._start_downloader_thread)

        self._line_edit = QtWidgets.QLineEdit()
        self._line_edit.set_style_sheet("QLineEdit{font-size: 15pt;}")
        self._line_edit.set_placeholder_text(translate("Select ffmpeg directory or download latest release"))
        self._line_edit.add_action(self.line_edit_action, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)

        if self._ffmpeg_path.exists():
            self._line_edit.insert(str(self._ffmpeg_path))

        page_title = QtWidgets.QLabel(translate("Setup converter"))
        page_title.set_style_sheet("QLabel{font-size: 25pt; padding-bottom: 20px;}")
        page_description = QtWidgets.QLabel(translate(
            "Select directory with ffmpeg, ffprobe and ffplay or download its latest release"
        ))
        page_description.set_style_sheet("QLabel{font-size: 12pt; padding-bottom: 20px;}")

        ffmpeg_hbox = QtWidgets.QHBoxLayout()
        ffmpeg_hbox.add_widget(self._download_button)
        ffmpeg_hbox.add_widget(self._line_edit)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.add_widget(page_title)
        self._layout.add_widget(page_description)
        self._layout.add_layout(ffmpeg_hbox)
        self._layout.add_widget(self._progress_bar)
        self.set_layout(self._layout)

    def _start_downloader_thread(self) -> None:
        self.wizard().button(QtWidgets.QWizard.WizardButton.BackButton).set_enabled(False)
        self._line_edit.set_disabled(True)
        self._download_button.set_disabled(True)
        self._download_thread.start(QThread.Priority.HighPriority)

    @Slot(int)
    def _show_downloader_progress(self, progress: int) -> None:
        self._progress_bar.set_value(progress)
        if round(progress, 0) >= 100:
            self._line_edit.set_disabled(False)
            self._download_button.set_disabled(False)
            self._progress_bar.set_value(0)

    @Slot(str)
    def _show_downloader_ready(self, ffmpeg_path: str) -> None:
        self._progress_bar.set_format(translate("Done!"))
        self._line_edit.set_focus()
        self._line_edit.clear()
        self._line_edit.insert(ffmpeg_path)
        self.wizard().button(QtWidgets.QWizard.WizardButton.BackButton).set_enabled(True)

    @Slot(str)
    def _download_worker_unpack(self, status: str) -> None:
        self._progress_bar.set_format(status)

    @Slot(str)
    def _unpack_ready(self, ffmpeg_path: str) -> None:
        self.wizard().button(QtWidgets.QWizard.WizardButton.NextButton).set_enabled(True)

    def is_complete(self) -> bool:
        return bool(self._ffmpeg_path.exists() if self._ffmpeg_path else False) and super().is_complete()

    def select_ffmpeg_root_path(self):
        ffmpeg_directory = QFileDialog.get_existing_directory(
            parent=self,
            caption=translate("Select ffmpeg directory"),
            dir=str(Global.USER_ROOT)
        )
        directory_path = QDir.to_native_separators(ffmpeg_directory)

        if directory_path:
            self.set_config(
                scope=Section.Root,
                section=Section.User,
                key="ffmpeg.root",
                data=directory_path
            )

            for binary in self._binaries:
                if not (directory_path / binary).exists():
                    raise FileNotFoundError(f"Binary file \"{binary.stem!s}\" not found. "
                                            f"Please, download ffmpeg bundle from https://ffmpeg.org/download.html")

                self.set_config(
                    scope=Section.Root,
                    section=Section.User,
                    key=f"ffmpeg.{binary.stem!s}",
                    data=str(directory_path / binary)
                )

            self.save_config(
                scope=Section.Root,
                section=Section.User
            )
            self._ffmpeg_path = Path(directory_path)
            self._line_edit.set_text(str(directory_path))
            self.completeChanged.emit()

    def finish(self) -> None:
        ffmpeg_path = Path(self._line_edit.text())
        # Converter root directory
        self.set_config(
            scope=Section.Root,
            section=Section.User,
            key="ffmpeg.root",
            data=str(ffmpeg_path)
        )
        # Default chunk size
        self.set_config(
            scope=Section.Root,
            section=Section.User,
            key="ffmpeg.chunk_size",
            data=10
        )
        # Binary extension name
        for binary in self._binaries:
            self.set_config(
                scope=Section.Root,
                section=Section.User,
                key=f"ffmpeg.{binary.stem}",
                data=str(binary)
            )

        # Default converter temporary folder
        self.set_config(
            scope=Section.Root,
            section=Section.User,
            key="ffmpeg.temp_folder",
            data=str(ffmpeg_path / Global.DEFAULT_TEMP_FOLDER_NAME)
        )

        self.save_config(Section.Root, Section.User)
