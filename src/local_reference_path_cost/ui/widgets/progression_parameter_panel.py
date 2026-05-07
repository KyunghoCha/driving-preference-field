from __future__ import annotations

from dataclasses import fields, replace

import numpy as np
from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
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

from local_reference_path_cost.config import FieldConfig
from local_reference_path_cost.progression_surface import longitudinal_profile_array, transverse_profile_array
from local_reference_path_cost.ui.help.catalog import ADVANCED_PARAMETER_GROUPS, MAIN_PARAMETER_KEYS, PARAMETER_SPECS, ParameterSpec
from local_reference_path_cost.ui.help.render import panel_note_text, progression_parameter_guide, section_title
from local_reference_path_cost.ui.locale import DEFAULT_LANGUAGE, t


MAIN_SECTION_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("longitudinal", ("longitudinal_frame", "longitudinal_family", "longitudinal_peak", "longitudinal_gain", "lookahead_scale", "longitudinal_shape")),
    ("transverse", ("transverse_family", "transverse_peak", "transverse_shape", "transverse_falloff")),
    ("support_gate", ("support_ceiling",)),
)


class _ProfilePreviewWidget(QWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE, title: str, tooltip_key: str) -> None:
        super().__init__()
        self._language = language
        self._title = title
        self._tooltip_key = tooltip_key
        self._config = FieldConfig()
        self.setMinimumHeight(140)
        self.setToolTip(t(language, tooltip_key))

    def minimumSizeHint(self) -> QSize:
        return QSize(220, 140)

    def sizeHint(self) -> QSize:
        return QSize(260, 150)

    def set_config(self, config: FieldConfig) -> None:
        self._config = config
        self.update()

    def set_language(self, language: str) -> None:
        self._language = language
        self.setToolTip(t(language, self._tooltip_key))
        self.update()

    def _series(self) -> tuple[np.ndarray, np.ndarray, tuple[str, str, str]]:
        raise NotImplementedError

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.fillRect(self.rect(), QColor("#ffffff"))
        outer = QRectF(self.rect()).adjusted(8.0, 8.0, -8.0, -8.0)
        painter.setPen(QPen(QColor("#d1d5db"), 1.0))
        painter.drawRoundedRect(outer, 8.0, 8.0)

        plot = outer.adjusted(28.0, 22.0, -12.0, -28.0)
        if plot.width() <= 10.0 or plot.height() <= 10.0:
            return

        x_values, y_values, tick_labels = self._series()
        y_max = max(float(np.max(y_values)), 1.0)

        painter.save()
        painter.setClipRect(plot)
        grid_pen = QPen(QColor("#eef2f7"), 1.0)
        painter.setPen(grid_pen)
        for ratio in np.linspace(0.0, 1.0, 9):
            x = plot.left() + ratio * plot.width()
            y = plot.top() + ratio * plot.height()
            painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
        painter.restore()

        x_min = float(np.min(x_values))
        x_max = float(np.max(x_values))

        def map_x(value: float) -> float:
            span = max(x_max - x_min, 1e-9)
            return float(plot.left() + ((value - x_min) / span) * plot.width())

        def map_y(value: float) -> float:
            return float(plot.bottom() - (value / y_max) * plot.height())

        axis_pen = QPen(QColor("#4b5563"), 1.2)
        painter.setPen(axis_pen)
        painter.drawLine(QPointF(plot.left(), plot.bottom()), QPointF(plot.right(), plot.bottom()))
        painter.drawLine(QPointF(plot.left(), plot.top()), QPointF(plot.left(), plot.bottom()))
        if x_min < 0.0 < x_max:
            center_x = map_x(0.0)
            painter.drawLine(QPointF(center_x, plot.top()), QPointF(center_x, plot.bottom()))

        curve = QPainterPath(QPointF(map_x(float(x_values[0])), map_y(float(y_values[0]))))
        for x_value, y_value in zip(x_values[1:], y_values[1:], strict=False):
            curve.lineTo(map_x(float(x_value)), map_y(float(y_value)))
        painter.setPen(QPen(QColor("#2563eb"), 2.0))
        painter.drawPath(curve)

        label_pen = QPen(QColor("#374151"), 1.0)
        painter.setPen(label_pen)
        title_rect = QRectF(outer.left() + 8.0, outer.top() + 4.0, outer.width() * 0.6, 16.0)
        max_rect = QRectF(outer.right() - 78.0, outer.top() + 4.0, 72.0, 16.0)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._title)
        painter.drawText(max_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"max={y_max:.2f}")

        tick_y0 = plot.bottom()
        tick_len = 6.0
        x_left = plot.left()
        x_mid = 0.5 * (plot.left() + plot.right())
        x_right = plot.right()
        for tick_x in (x_left, x_mid, x_right):
            painter.drawLine(QPointF(tick_x, tick_y0), QPointF(tick_x, tick_y0 + tick_len))
        painter.drawLine(QPointF(plot.left() - tick_len, plot.bottom()), QPointF(plot.left(), plot.bottom()))
        painter.drawLine(QPointF(plot.left() - tick_len, plot.top()), QPointF(plot.left(), plot.top()))

        painter.drawText(
            QRectF(plot.left() - 8.0, plot.bottom() + 6.0, 44.0, 16.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            tick_labels[0],
        )
        painter.drawText(
            QRectF(x_mid - 18.0, plot.bottom() + 6.0, 36.0, 16.0),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            tick_labels[1],
        )
        painter.drawText(
            QRectF(plot.right() - 40.0, plot.bottom() + 6.0, 44.0, 16.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
            tick_labels[2],
        )
        painter.drawText(
            QRectF(plot.left() - 24.0, plot.bottom() - 8.0, 20.0, 16.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            "0",
        )
        painter.drawText(
            QRectF(plot.left() - 24.0, plot.top() - 8.0, 20.0, 16.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            f"{y_max:.1f}",
        )

class _TransverseProfilePreviewWidget(_ProfilePreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, title="T(|r|), r[m]", tooltip_key="param.preview.transverse_tooltip")

    def _series(self) -> tuple[np.ndarray, np.ndarray, tuple[str, str, str]]:
        progression = self._config.progression
        half_width = 3.0
        x_values = np.linspace(-half_width, half_width, 241, dtype=float)
        y_values = transverse_profile_array(x_values, progression)
        return x_values, y_values, (f"{-half_width:.1f}m", "0", f"{half_width:.1f}m")


class _LongitudinalProfilePreviewWidget(_ProfilePreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, title="L(u), u∈[0,1]", tooltip_key="param.preview.longitudinal_tooltip")

    def _series(self) -> tuple[np.ndarray, np.ndarray, tuple[str, str, str]]:
        progression = self._config.progression
        x_values = np.linspace(0.0, 1.0, 241, dtype=float)
        y_values = longitudinal_profile_array(x_values, progression)
        return x_values, y_values, ("0", "0.5", "1.0")


class _LookaheadProfilePreviewWidget(_ProfilePreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, title="blend(τ/span)", tooltip_key="param.preview.lookahead_tooltip")

    def _series(self) -> tuple[np.ndarray, np.ndarray, tuple[str, str, str]]:
        lookahead = max(float(self._config.progression.lookahead_scale), 1e-6)
        x_values = np.linspace(-1.0, 1.0, 241, dtype=float)
        y_values = np.exp(-0.5 * (x_values / lookahead) ** 2)
        return x_values, y_values, ("-1.0", "0", "1.0")


class _SummaryPreviewWidget(QLabel):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE, tooltip_key: str) -> None:
        super().__init__()
        self._language = language
        self._tooltip_key = tooltip_key
        self._config = FieldConfig()
        self.setWordWrap(True)
        self.setMinimumHeight(56)
        self.setStyleSheet(
            "background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; "
            "padding: 8px; color: #374151;"
        )
        self.setToolTip(t(language, tooltip_key))

    def set_config(self, config: FieldConfig) -> None:
        self._config = config
        self._refresh()

    def set_language(self, language: str) -> None:
        self._language = language
        self.setToolTip(t(language, self._tooltip_key))
        self._refresh()

    def _summary_lines(self) -> tuple[str, ...]:
        raise NotImplementedError

    def _refresh(self) -> None:
        self.setText("\n".join(self._summary_lines()))


class _SupportSummaryWidget(_SummaryPreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, tooltip_key="param.preview.summary_tooltip")

    def _summary_lines(self) -> tuple[str, ...]:
        progression = self._config.progression
        return (
            f"cap = {progression.support_ceiling:.2f}",
            f"effective confidence <= {progression.support_ceiling:.2f}",
        )


class _LongitudinalMixSummaryWidget(_SummaryPreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, tooltip_key="param.preview.summary_tooltip")

    def _summary_lines(self) -> tuple[str, ...]:
        progression = self._config.progression
        u_values = np.linspace(0.0, 1.0, 129, dtype=float)
        function_max = float(np.max(longitudinal_profile_array(u_values, progression)))
        return (
            f"gain = {progression.longitudinal_gain:.2f}",
            f"weighted max ≈ {progression.longitudinal_gain * function_max:.2f}",
        )


class _DiscretizationSummaryWidget(_SummaryPreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, tooltip_key="param.preview.summary_tooltip")

    def _summary_lines(self) -> tuple[str, ...]:
        tuning = self._config.surface_tuning
        anchor_density = 1.0 / max(tuning.anchor_spacing_m, 1e-6)
        spline_density = 1.0 / max(tuning.spline_sample_density_m, 1e-6)
        return (
            f"anchors ≈ {anchor_density:.1f} / m",
            f"spline ≈ {spline_density:.1f} / m",
            f"end ext = {tuning.end_extension_m:.2f} m",
        )


class _KernelSummaryWidget(_SummaryPreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, tooltip_key="param.preview.summary_tooltip")

    def _summary_lines(self) -> tuple[str, ...]:
        tuning = self._config.surface_tuning
        progression = self._config.progression
        return (
            f"σ_t floor = {tuning.min_sigma_t:.2f}, span coeff = {progression.lookahead_scale * tuning.sigma_t_scale:.3f}",
            f"σ_n floor = {tuning.min_sigma_n:.2f}, scale coeff = {tuning.sigma_n_scale:.2f}",
        )


class _ModulationSummaryWidget(_SummaryPreviewWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__(language=language, tooltip_key="param.preview.summary_tooltip")

    def _summary_lines(self) -> tuple[str, ...]:
        tuning = self._config.surface_tuning
        support_hi = tuning.support_base + tuning.support_range
        align_hi = tuning.alignment_base + tuning.alignment_range
        return (
            f"support ∈ [{tuning.support_base:.2f}, {support_hi:.2f}]",
            f"align ∈ [{tuning.alignment_base:.2f}, {align_hi:.2f}]",
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
        self._summary_label_widgets: dict[str, QLabel] = {}
        self._summary_widgets: dict[str, _SummaryPreviewWidget] = {}

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
        self._longitudinal_profile_preview = _LongitudinalProfilePreviewWidget(language=language)
        self._longitudinal_preview_label = QLabel()
        self._longitudinal_preview_label.setToolTip(t(language, "param.preview.longitudinal_tooltip"))
        longitudinal_form.addRow(self._longitudinal_preview_label, self._longitudinal_profile_preview)
        self._longitudinal_summary_preview = _LongitudinalMixSummaryWidget(language=language)
        self._longitudinal_summary_label = QLabel()
        self._longitudinal_summary_label.setToolTip(t(language, "param.preview.summary_tooltip"))
        longitudinal_form.addRow(self._longitudinal_summary_label, self._longitudinal_summary_preview)
        self._summary_label_widgets["longitudinal_mix"] = self._longitudinal_summary_label
        self._summary_widgets["longitudinal_mix"] = self._longitudinal_summary_preview
        self._lookahead_profile_preview = _LookaheadProfilePreviewWidget(language=language)
        self._lookahead_preview_label = QLabel()
        self._lookahead_preview_label.setToolTip(t(language, "param.preview.lookahead_tooltip"))
        longitudinal_form.addRow(self._lookahead_preview_label, self._lookahead_profile_preview)
        self._transverse_profile_preview = _TransverseProfilePreviewWidget(language=language)
        self._transverse_preview_label = QLabel()
        self._transverse_preview_label.setToolTip(t(language, "param.preview.transverse_tooltip"))
        transverse_form.addRow(self._transverse_preview_label, self._transverse_profile_preview)
        self._support_summary_preview = _SupportSummaryWidget(language=language)
        self._support_summary_label = QLabel()
        self._support_summary_label.setToolTip(t(language, "param.preview.summary_tooltip"))
        support_form.addRow(self._support_summary_label, self._support_summary_preview)
        self._summary_label_widgets["support_gate"] = self._support_summary_label
        self._summary_widgets["support_gate"] = self._support_summary_preview

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
            summary_widget: _SummaryPreviewWidget | None = None
            if group_key == "discretization":
                summary_widget = _DiscretizationSummaryWidget(language=language)
            elif group_key == "support_kernel":
                summary_widget = _KernelSummaryWidget(language=language)
            elif group_key == "modulation":
                summary_widget = _ModulationSummaryWidget(language=language)
            if summary_widget is not None:
                summary_label = QLabel()
                summary_label.setToolTip(t(language, "param.preview.summary_tooltip"))
                form.addRow(summary_label, summary_widget)
                self._summary_label_widgets[group_key] = summary_label
                self._summary_widgets[group_key] = summary_widget
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
        self._longitudinal_profile_preview.set_config(self._pending_config)
        self._lookahead_profile_preview.set_config(self._pending_config)
        self._transverse_profile_preview.set_config(self._pending_config)
        for widget in self._summary_widgets.values():
            widget.set_config(self._pending_config)
        self._apply_button.setEnabled(False)
        self._reset_button.setEnabled(False)

    def _on_changed(self) -> None:
        self._pending_config = self._build_config_from_controls()
        self._longitudinal_profile_preview.set_config(self._pending_config)
        self._lookahead_profile_preview.set_config(self._pending_config)
        self._transverse_profile_preview.set_config(self._pending_config)
        for widget in self._summary_widgets.values():
            widget.set_config(self._pending_config)
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
        self._longitudinal_preview_label.setText(t(language, "param.preview.longitudinal"))
        self._longitudinal_preview_label.setToolTip(t(language, "param.preview.longitudinal_tooltip"))
        self._longitudinal_profile_preview.set_language(language)
        self._lookahead_preview_label.setText(t(language, "param.preview.lookahead"))
        self._lookahead_preview_label.setToolTip(t(language, "param.preview.lookahead_tooltip"))
        self._lookahead_profile_preview.set_language(language)
        self._transverse_preview_label.setText(t(language, "param.preview.transverse"))
        self._transverse_preview_label.setToolTip(t(language, "param.preview.transverse_tooltip"))
        self._transverse_profile_preview.set_language(language)
        for section_key, label in self._summary_label_widgets.items():
            label.setText(t(language, "param.preview.summary"))
            label.setToolTip(t(language, "param.preview.summary_tooltip"))
            self._summary_widgets[section_key].set_language(language)
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
