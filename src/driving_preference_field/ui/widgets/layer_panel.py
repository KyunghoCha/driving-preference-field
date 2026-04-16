from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QVBoxLayout, QWidget


LAYER_LABELS = {
    "progression_guides": "Progression guides",
    "drivable_boundary": "Drivable boundary",
    "ego": "Ego pose",
    "hard_masks": "Hard masks",
}


class LayerPanelWidget(QWidget):
    visibilityChanged = pyqtSignal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._checkboxes: dict[str, QCheckBox] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        for key, label in LAYER_LABELS.items():
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, layer_key=key: self.visibilityChanged.emit(layer_key, checked))
            self._checkboxes[key] = checkbox
            layout.addWidget(checkbox)
        layout.addStretch(1)

    def visibility(self) -> dict[str, bool]:
        return {key: checkbox.isChecked() for key, checkbox in self._checkboxes.items()}
