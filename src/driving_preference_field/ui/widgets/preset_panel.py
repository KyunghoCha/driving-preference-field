from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QListWidgetItem,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from driving_preference_field.presets import PresetDescriptor
from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t


class PresetPanelWidget(QWidget):
    loadRequested = pyqtSignal(str, str)
    saveRequested = pyqtSignal(str, str)
    copyRequested = pyqtSignal(str, str)

    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self._lists = {
            "baseline": QListWidget(),
            "candidate": QListWidget(),
        }
        for list_widget in self._lists.values():
            list_widget.setMinimumWidth(0)
            list_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.addTab(self._lists["baseline"], "")
        self._tabs.addTab(self._lists["candidate"], "")
        self._save_baseline = QPushButton()
        self._save_candidate = QPushButton()
        self._load_baseline = QPushButton()
        self._load_candidate = QPushButton()
        self._copy_b_to_c = QPushButton()
        self._copy_c_to_b = QPushButton()

        layout = QVBoxLayout(self)
        layout.addWidget(self._tabs)
        layout.addWidget(self._load_baseline)
        layout.addWidget(self._load_candidate)
        layout.addWidget(self._save_baseline)
        layout.addWidget(self._save_candidate)
        row = QHBoxLayout()
        row.addWidget(self._copy_c_to_b)
        row.addWidget(self._copy_b_to_c)
        layout.addLayout(row)

        self._load_baseline.clicked.connect(lambda: self._emit_load("baseline"))
        self._load_candidate.clicked.connect(lambda: self._emit_load("candidate"))
        self._save_baseline.clicked.connect(lambda: self._emit_save("baseline"))
        self._save_candidate.clicked.connect(lambda: self._emit_save("candidate"))
        self._copy_b_to_c.clicked.connect(lambda: self.copyRequested.emit("baseline", "candidate"))
        self._copy_c_to_b.clicked.connect(lambda: self.copyRequested.emit("candidate", "baseline"))

        for button in (
            self._save_baseline,
            self._save_candidate,
            self._load_baseline,
            self._load_candidate,
            self._copy_b_to_c,
            self._copy_c_to_b,
        ):
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.retranslate(language)

    def set_presets(
        self,
        *,
        baseline_presets: list[PresetDescriptor],
        candidate_presets: list[PresetDescriptor],
    ) -> None:
        self._populate_list("baseline", baseline_presets)
        self._populate_list("candidate", candidate_presets)

    def _populate_list(self, side: str, descriptors: list[PresetDescriptor]) -> None:
        list_widget = self._lists[side]
        list_widget.clear()
        for descriptor in descriptors:
            item = QListWidgetItem(descriptor.display_name)
            item.setData(Qt.ItemDataRole.UserRole, str(descriptor.path))
            tooltip = descriptor.description or descriptor.path.name
            item.setToolTip(f"{tooltip}\nrole={descriptor.role or '-'} | family={descriptor.family}")
            list_widget.addItem(item)
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)

    def _emit_load(self, target: str) -> None:
        item = self._lists[target].currentItem()
        if item is None:
            return
        preset_path = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(preset_path, str):
            return
        self.loadRequested.emit(target, preset_path)

    def _emit_save(self, source: str) -> None:
        preset_name, accepted = QInputDialog.getText(
            self,
            t(self._language, "preset.save_dialog.title"),
            t(self._language, "preset.save_dialog.label"),
        )
        if accepted and preset_name.strip():
            self.saveRequested.emit(source, preset_name.strip())

    def retranslate(self, language: str) -> None:
        self._language = language
        self._tabs.setTabText(0, t(language, "tab.baseline"))
        self._tabs.setTabText(1, t(language, "tab.candidate"))
        self._save_baseline.setText(t(language, "preset.save_baseline"))
        self._save_candidate.setText(t(language, "preset.save_candidate"))
        self._load_baseline.setText(t(language, "preset.load_baseline"))
        self._load_candidate.setText(t(language, "preset.load_candidate"))
        self._copy_b_to_c.setText(t(language, "preset.copy_b_to_c"))
        self._copy_c_to_b.setText(t(language, "preset.copy_c_to_b"))
