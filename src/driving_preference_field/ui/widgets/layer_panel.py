from __future__ import annotations

from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QSizePolicy, QVBoxLayout, QWidget

from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t

LAYER_LABEL_KEYS = {
    "progression_guides": "layer.progression_guides",
    "progression_targets": "layer.progression_targets",
    "drivable_boundary": "layer.drivable_boundary",
    "ego": "layer.ego",
    "hard_masks": "layer.hard_masks",
}


class LayerPanelWidget(QWidget):
    visibilityChanged = pyqtSignal(str, bool)

    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self._checkboxes: dict[str, QCheckBox] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        for key in LAYER_LABEL_KEYS:
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, layer_key=key: self.visibilityChanged.emit(layer_key, checked))
            self._checkboxes[key] = checkbox
            layout.addWidget(checkbox)
        layout.addStretch(1)
        self.retranslate(language)

    def minimumSizeHint(self) -> QSize:
        return QSize(160, 120)

    def sizeHint(self) -> QSize:
        return QSize(220, 180)

    def visibility(self) -> dict[str, bool]:
        return {key: checkbox.isChecked() for key, checkbox in self._checkboxes.items()}

    def retranslate(self, language: str) -> None:
        self._language = language
        for key, checkbox in self._checkboxes.items():
            checkbox.setText(t(language, LAYER_LABEL_KEYS[key]))
