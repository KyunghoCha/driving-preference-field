from __future__ import annotations

from dataclasses import fields, replace

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from driving_preference_field.config import FieldConfig
from driving_preference_field.ui.help.catalog import ADVANCED_PARAMETER_GROUPS, MAIN_PARAMETER_KEYS, PARAMETER_SPECS, ParameterSpec
from driving_preference_field.ui.help.render import panel_note_text, progression_parameter_guide, section_title
from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t


MAIN_SECTION_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("longitudinal", ("longitudinal_frame", "longitudinal_family", "longitudinal_gain", "lookahead_scale", "longitudinal_shape")),
    ("transverse", ("transverse_family", "transverse_scale", "transverse_shape")),
    ("support_gate", ("support_ceiling",)),
)


class ProgressionParameterPanelWidget(QWidget):
    configApplied = pyqtSignal(object)
    helpRequested = pyqtSignal()

    def __init__(self, *, title: str, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self._title = title
        self._config = FieldConfig()
        self._pending_config = FieldConfig()
        self._controls: dict[str, QWidget] = {}
        self._label_widgets: dict[str, QLabel] = {}
        self._advanced_group_widgets: dict[str, QGroupBox] = {}

        layout = QVBoxLayout(self)
        self._root_group = QGroupBox(title)
        root_layout = QVBoxLayout(self._root_group)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        self._longitudinal_group, longitudinal_form = self._build_section(section_title(language, "longitudinal"))
        self._transverse_group, transverse_form = self._build_section(section_title(language, "transverse"))
        self._support_group, support_form = self._build_section(section_title(language, "support_gate"))
        section_forms = {
            "longitudinal": longitudinal_form,
            "transverse": transverse_form,
            "support_gate": support_form,
        }
        for section_key, keys in MAIN_SECTION_KEYS:
            form = section_forms[section_key]
            for key in keys:
                control = self._build_control(key)
                self._controls[key] = control
                setattr(self, f"_{key}", control)
                form.addRow(self._make_label(key), control)

        root_layout.addWidget(self._longitudinal_group)
        root_layout.addWidget(self._transverse_group)
        root_layout.addWidget(self._support_group)

        self._advanced_toggle = QToolButton()
        self._advanced_toggle.setCheckable(True)
        self._advanced_toggle.setChecked(False)
        self._advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self._advanced_toggle.toggled.connect(self._set_advanced_visible)
        root_layout.addWidget(self._advanced_toggle)

        self._advanced_content = QWidget()
        self._advanced_content_layout = QVBoxLayout(self._advanced_content)
        self._advanced_content_layout.setContentsMargins(0, 0, 0, 0)
        self._advanced_content_layout.setSpacing(8)
        for group_key, keys in ADVANCED_PARAMETER_GROUPS:
            group, form = self._build_section(section_title(language, group_key))
            self._advanced_group_widgets[group_key] = group
            for key in keys:
                control = self._build_control(key)
                self._controls[key] = control
                setattr(self, f"_{key}", control)
                form.addRow(self._make_label(key), control)
            self._advanced_content_layout.addWidget(group)
        self._advanced_content_layout.addStretch(1)
        self._advanced_content.setVisible(False)
        root_layout.addWidget(self._advanced_content)

        self._note_label = QLabel()
        self._note_label.setWordWrap(True)
        self._note_label.setStyleSheet("color: #555; font-size: 11px;")
        root_layout.addWidget(self._note_label)

        self._apply_button = QPushButton()
        self._reset_button = QPushButton()
        self._help_button = QPushButton()
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
        layout.addWidget(self._root_group)
        layout.addStretch(1)

        self.retranslate(language, title=title)
        self.set_config(self._config)

    def _build_section(self, title: str) -> tuple[QGroupBox, QFormLayout]:
        group = QGroupBox(title)
        form = QFormLayout(group)
        form.setContentsMargins(8, 8, 8, 8)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        return group, form

    def _build_control(self, key: str) -> QWidget:
        spec = PARAMETER_SPECS[key]
        if spec.widget_kind == "combo":
            control = QComboBox()
            control.addItems(spec.options)
            control.currentTextChanged.connect(self._on_changed)
        elif spec.widget_kind == "spin":
            control = QSpinBox()
            assert spec.numeric_range is not None
            control.setRange(int(spec.numeric_range[0]), int(spec.numeric_range[1]))
            control.setSingleStep(int(spec.single_step))
            control.valueChanged.connect(self._on_changed)
        else:
            control = QDoubleSpinBox()
            assert spec.numeric_range is not None
            control.setDecimals(spec.decimals)
            control.setRange(float(spec.numeric_range[0]), float(spec.numeric_range[1]))
            control.setSingleStep(spec.single_step)
            control.valueChanged.connect(self._on_changed)
        control.setMinimumWidth(spec.minimum_width)
        return control

    def _guide_entry(self, key: str):
        return progression_parameter_guide(self._language)[key]

    def _control_tooltip(self, key: str) -> str:
        entry = self._guide_entry(key)
        return (
            f"{entry.tooltip}\n"
            f"Practical band: {entry.practical_band}\n"
            f"Technical range: {entry.technical_range}"
        )

    def _label_text(self, key: str) -> str:
        entry = self._guide_entry(key)
        if PARAMETER_SPECS[key].widget_kind == "combo":
            return entry.label
        return f"{entry.label} [{entry.practical_band.replace(' .. ', '-')}]"

    def _make_label(self, key: str) -> QLabel:
        label = QLabel(self._label_text(key))
        self._label_widgets[key] = label
        self._update_label_tooltip(key)
        self._update_control_tooltip(key)
        return label

    def _update_label_tooltip(self, key: str) -> None:
        label = self._label_widgets[key]
        entry = self._guide_entry(key)
        label.setToolTip(
            f"{entry.meaning}\n"
            f"Practical band: {entry.practical_band}\n"
            f"Technical range: {entry.technical_range}"
        )

    def _update_control_tooltip(self, key: str) -> None:
        self._controls[key].setToolTip(self._control_tooltip(key))

    def _set_advanced_visible(self, visible: bool) -> None:
        self._advanced_content.setVisible(visible)
        self._advanced_toggle.setArrowType(Qt.ArrowType.DownArrow if visible else Qt.ArrowType.RightArrow)

    def config(self) -> FieldConfig:
        return self._config

    def pending_config(self) -> FieldConfig:
        return self._pending_config

    def set_config(self, config: FieldConfig) -> None:
        self._config = config
        self._pending_config = config
        for key, control in self._controls.items():
            control.blockSignals(True)
            spec = PARAMETER_SPECS[key]
            source = config.progression if spec.config_namespace == "progression" else config.surface_tuning
            value = getattr(source, key)
            if isinstance(control, QComboBox):
                control.setCurrentText(str(value))
            elif isinstance(control, QSpinBox):
                control.setValue(int(value))
            else:
                control.setValue(float(value))
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

    def retranslate(self, language: str, *, title: str | None = None) -> None:
        self._language = language
        if title is not None:
            self._title = title
        self._root_group.setTitle(self._title)
        self._longitudinal_group.setTitle(section_title(language, "longitudinal"))
        self._transverse_group.setTitle(section_title(language, "transverse"))
        self._support_group.setTitle(section_title(language, "support_gate"))
        self._advanced_toggle.setText(section_title(language, "advanced"))
        for group_key, group in self._advanced_group_widgets.items():
            group.setTitle(section_title(language, group_key))
        for key, label in self._label_widgets.items():
            label.setText(self._label_text(key))
            self._update_label_tooltip(key)
            self._update_control_tooltip(key)
        self._note_label.setText(panel_note_text(language))
        self._apply_button.setText(t(language, "param.button.apply"))
        self._reset_button.setText(t(language, "param.button.reset"))
        self._help_button.setText(t(language, "param.button.help"))

    def _build_config_from_controls(self) -> FieldConfig:
        progression_updates: dict[str, object] = {}
        surface_updates: dict[str, object] = {}
        for key, control in self._controls.items():
            spec: ParameterSpec = PARAMETER_SPECS[key]
            if isinstance(control, QComboBox):
                value: object = control.currentText()
            elif isinstance(control, QSpinBox):
                value = int(control.value())
            else:
                value = float(control.value())
            target = progression_updates if spec.config_namespace == "progression" else surface_updates
            target[key] = value

        progression = replace(self._config.progression, **progression_updates)
        surface_tuning = replace(self._config.surface_tuning, **surface_updates)
        return replace(self._config, progression=progression, surface_tuning=surface_tuning)
