from __future__ import annotations

from dataclasses import replace

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from driving_preference_field.config import FieldConfig
from driving_preference_field.ui.parameter_guide import (
    PANEL_NOTE_TEXT,
    PROGRESSION_PARAMETER_GUIDE,
)


class ProgressionParameterPanelWidget(QWidget):
    configApplied = pyqtSignal(object)
    helpRequested = pyqtSignal()

    def __init__(self, *, title: str) -> None:
        super().__init__()
        self._config = FieldConfig()
        self._pending_config = FieldConfig()
        self._controls: dict[str, object] = {}
        layout = QVBoxLayout(self)
        root_group = QGroupBox(title)
        root_layout = QVBoxLayout(root_group)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        longitudinal_group, longitudinal_form = self._build_section("Longitudinal")
        transverse_group, transverse_form = self._build_section("Transverse")
        support_group, support_form = self._build_section("Support / Gate")

        self._longitudinal_family = QComboBox()
        self._longitudinal_frame = QComboBox()
        self._longitudinal_frame.addItems(["local_absolute", "ego_relative"])
        self._longitudinal_frame.currentTextChanged.connect(self._on_changed)
        long_frame_guide = PROGRESSION_PARAMETER_GUIDE["longitudinal_frame"]
        self._longitudinal_frame.setToolTip(
            f"{long_frame_guide.tooltip}\nRange: {long_frame_guide.technical_range}"
        )
        longitudinal_form.addRow(self._make_label("longitudinal_frame"), self._longitudinal_frame)
        self._controls["longitudinal_frame"] = self._longitudinal_frame

        self._longitudinal_family = QComboBox()
        self._longitudinal_family.addItems(["tanh", "linear", "inverse", "power"])
        self._longitudinal_family.currentTextChanged.connect(self._on_changed)
        long_family_guide = PROGRESSION_PARAMETER_GUIDE["longitudinal_family"]
        self._longitudinal_family.setToolTip(
            f"{long_family_guide.tooltip}\nRange: {long_family_guide.technical_range}"
        )
        longitudinal_form.addRow(self._make_label("longitudinal_family"), self._longitudinal_family)
        self._controls["longitudinal_family"] = self._longitudinal_family

        for key in ("longitudinal_gain", "lookahead_scale", "longitudinal_shape"):
            spin = QDoubleSpinBox()
            spin.setDecimals(4)
            spin.setRange(0.0, 1000.0)
            spin.setSingleStep(0.05)
            spin.setMinimumWidth(120)
            spin.valueChanged.connect(self._on_changed)
            guide = PROGRESSION_PARAMETER_GUIDE[key]
            spin.setToolTip(
                f"{guide.tooltip}\n"
                f"Practical band: {guide.practical_band}\n"
                f"Technical range: {guide.technical_range}"
            )
            self._controls[key] = spin
            longitudinal_form.addRow(self._make_label(key), spin)

        self._transverse_family = QComboBox()
        self._transverse_family.addItems(["exponential", "inverse", "power"])
        self._transverse_family.currentTextChanged.connect(self._on_changed)
        transverse_family_guide = PROGRESSION_PARAMETER_GUIDE["transverse_family"]
        self._transverse_family.setToolTip(
            f"{transverse_family_guide.tooltip}\nRange: {transverse_family_guide.technical_range}"
        )
        transverse_form.addRow(self._make_label("transverse_family"), self._transverse_family)
        self._controls["transverse_family"] = self._transverse_family

        for key in ("transverse_scale", "transverse_shape"):
            spin = QDoubleSpinBox()
            spin.setDecimals(4)
            spin.setRange(0.0, 1000.0)
            spin.setSingleStep(0.05)
            spin.setMinimumWidth(120)
            spin.valueChanged.connect(self._on_changed)
            guide = PROGRESSION_PARAMETER_GUIDE[key]
            spin.setToolTip(
                f"{guide.tooltip}\n"
                f"Practical band: {guide.practical_band}\n"
                f"Technical range: {guide.technical_range}"
            )
            self._controls[key] = spin
            transverse_form.addRow(self._make_label(key), spin)

        for key in ("support_ceiling",):
            spin = QDoubleSpinBox()
            spin.setDecimals(4)
            spin.setRange(0.0, 1000.0)
            spin.setSingleStep(0.05)
            spin.setMinimumWidth(120)
            spin.valueChanged.connect(self._on_changed)
            guide = PROGRESSION_PARAMETER_GUIDE[key]
            spin.setToolTip(
                f"{guide.tooltip}\n"
                f"Practical band: {guide.practical_band}\n"
                f"Technical range: {guide.technical_range}"
            )
            self._controls[key] = spin
            support_form.addRow(self._make_label(key), spin)

        root_layout.addWidget(longitudinal_group)
        root_layout.addWidget(transverse_group)
        root_layout.addWidget(support_group)
        self._note_label = QLabel(PANEL_NOTE_TEXT)
        self._note_label.setWordWrap(True)
        self._note_label.setStyleSheet("color: #555; font-size: 11px;")
        root_layout.addWidget(self._note_label)
        self._apply_button = QPushButton("Apply")
        self._reset_button = QPushButton("Reset")
        self._help_button = QPushButton("Help")
        self._apply_button.setEnabled(False)
        self._apply_button.clicked.connect(self.apply_pending)
        self._reset_button.setEnabled(False)
        self._reset_button.clicked.connect(self.reset_pending)
        self._help_button.clicked.connect(self.helpRequested.emit)
        actions = QHBoxLayout()
        actions.addWidget(self._reset_button)
        actions.addWidget(self._help_button)
        actions.addWidget(self._apply_button)
        root_layout.addLayout(actions)
        layout.addWidget(root_group)
        layout.addStretch(1)
        self.set_config(self._config)

    def _build_section(self, title: str) -> tuple[QGroupBox, QFormLayout]:
        group = QGroupBox(title)
        form = QFormLayout(group)
        form.setContentsMargins(8, 8, 8, 8)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        return group, form

    def _make_label(self, key: str) -> QLabel:
        guide = PROGRESSION_PARAMETER_GUIDE[key]
        if key in {"longitudinal_frame", "longitudinal_family", "transverse_family"}:
            text = guide.label
        else:
            compact_band = guide.practical_band.replace(" .. ", "-")
            text = f"{guide.label} [{compact_band}]"
        label = QLabel(text)
        label.setToolTip(
            f"{guide.meaning}\n"
            f"Practical band: {guide.practical_band}\n"
            f"Technical range: {guide.technical_range}"
        )
        return label

    def config(self) -> FieldConfig:
        return self._config

    def pending_config(self) -> FieldConfig:
        return self._pending_config

    def set_config(self, config: FieldConfig) -> None:
        self._config = config
        self._pending_config = config
        progression = config.progression
        self._longitudinal_frame.blockSignals(True)
        self._longitudinal_frame.setCurrentText(progression.longitudinal_frame)
        self._longitudinal_frame.blockSignals(False)
        self._longitudinal_family.blockSignals(True)
        self._longitudinal_family.setCurrentText(progression.longitudinal_family)
        self._longitudinal_family.blockSignals(False)
        self._transverse_family.blockSignals(True)
        self._transverse_family.setCurrentText(progression.transverse_family)
        self._transverse_family.blockSignals(False)
        for key, control in self._controls.items():
            if key in {"longitudinal_frame", "longitudinal_family", "transverse_family"}:
                continue
            control.blockSignals(True)
            control.setValue(float(getattr(progression, key)))
            control.blockSignals(False)
        self._apply_button.setEnabled(False)
        self._reset_button.setEnabled(False)

    def _on_changed(self) -> None:
        self._pending_config = self._build_config_from_controls()
        changed = self._pending_config != self._config
        self._apply_button.setEnabled(changed)
        self._reset_button.setEnabled(changed)

    def apply_pending(self) -> None:
        self._pending_config = self._build_config_from_controls()
        if self._pending_config == self._config:
            self._apply_button.setEnabled(False)
            self._reset_button.setEnabled(False)
            return
        self._config = self._pending_config
        self._apply_button.setEnabled(False)
        self._reset_button.setEnabled(False)
        self.configApplied.emit(self._config)

    def reset_pending(self) -> None:
        self.set_config(self._config)

    def _build_config_from_controls(self) -> FieldConfig:
        progression = self._config.progression
        updated = replace(
            progression,
            longitudinal_frame=self._longitudinal_frame.currentText(),
            longitudinal_family=self._longitudinal_family.currentText(),
            longitudinal_gain=self._controls["longitudinal_gain"].value(),
            lookahead_scale=self._controls["lookahead_scale"].value(),
            longitudinal_shape=self._controls["longitudinal_shape"].value(),
            transverse_family=self._transverse_family.currentText(),
            transverse_scale=self._controls["transverse_scale"].value(),
            transverse_shape=self._controls["transverse_shape"].value(),
            support_ceiling=self._controls["support_ceiling"].value(),
        )
        return replace(self._config, progression=updated)
