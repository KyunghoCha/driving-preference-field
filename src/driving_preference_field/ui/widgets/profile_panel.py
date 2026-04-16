from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from driving_preference_field.contracts import QueryContext
from driving_preference_field.profile_contracts import ProfileSpec
from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t

if TYPE_CHECKING:
    from driving_preference_field.profile_contracts import ComparisonProfileResult


LOGGER = logging.getLogger(__name__)


class _ProfileImageWidget(QWidget):
    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self._has_pixmap = False
        self._empty_text = t(language, "profile.no_result")
        self._label = QLabel(self._empty_text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumSize(0, 0)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._scroll = QScrollArea()
        self._scroll.setWidget(self._label)
        self._scroll.setWidgetResizable(False)
        self._scroll.setMinimumWidth(0)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll)

    def minimumSizeHint(self) -> QSize:
        return QSize(120, 120)

    def sizeHint(self) -> QSize:
        return QSize(220, 180)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._has_pixmap:
            self._resize_placeholder_to_viewport()

    def set_png(self, payload: bytes | None, *, empty_text: str | None = None) -> None:
        if empty_text is not None:
            self._empty_text = empty_text
        if not payload:
            self._has_pixmap = False
            self._label.setText(self._empty_text)
            self._label.setPixmap(QPixmap())
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._label.setMinimumSize(0, 0)
            self._resize_placeholder_to_viewport()
            return
        self._label.setText("")
        pixmap = QPixmap()
        pixmap.loadFromData(payload)
        self._has_pixmap = True
        self._label.setPixmap(pixmap)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._label.setMinimumSize(pixmap.size())
        self._label.setMaximumSize(pixmap.size())
        self._label.resize(pixmap.size())

    def retranslate(self, language: str) -> None:
        self._language = language
        if not self._has_pixmap:
            self._empty_text = t(language, "profile.no_result")
            self._label.setText(self._empty_text)

    def _resize_placeholder_to_viewport(self) -> None:
        viewport_size = self._scroll.viewport().size()
        width = max(1, viewport_size.width())
        height = max(1, viewport_size.height())
        placeholder_size = QSize(width, height)
        self._label.setMinimumSize(placeholder_size)
        self._label.setMaximumSize(placeholder_size)
        self._label.resize(placeholder_size)


class ProfilePanelWidget(QWidget):
    profileSpecChanged = pyqtSignal(str, float)

    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self._context: QueryContext | None = None
        self._axis_selector = QComboBox()
        self._coordinate_spin = QDoubleSpinBox()
        self._coordinate_spin.setDecimals(3)
        self._coordinate_spin.setSingleStep(0.1)
        self._ego_button = QPushButton()
        self._center_button = QPushButton()
        self._line_label = QLabel()
        self._line_label.setWordWrap(True)
        self._line_label.setMinimumWidth(0)
        self._line_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self._tabs = QTabWidget()
        self._tabs.setMinimumWidth(0)
        self._tabs.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._baseline_widget = _ProfileImageWidget(language=language)
        self._candidate_widget = _ProfileImageWidget(language=language)
        self._diff_widget = _ProfileImageWidget(language=language)
        self._tabs.addTab(self._baseline_widget, "")
        self._tabs.addTab(self._candidate_widget, "")
        self._tabs.addTab(self._diff_widget, "")
        self._line_control_label = QLabel()
        self._coord_control_label = QLabel()

        controls = QGridLayout()
        controls.addWidget(self._line_control_label, 0, 0)
        controls.addWidget(self._axis_selector, 0, 1)
        controls.addWidget(self._coord_control_label, 1, 0)
        controls.addWidget(self._coordinate_spin, 1, 1)
        controls.addWidget(self._ego_button, 2, 0)
        controls.addWidget(self._center_button, 2, 1)
        controls.setColumnStretch(1, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self._line_label)
        layout.addWidget(self._tabs, 1)

        self._axis_selector.currentIndexChanged.connect(self._on_axis_changed)
        self._coordinate_spin.valueChanged.connect(self._emit_spec_changed)
        self._ego_button.clicked.connect(self._set_to_ego)
        self._center_button.clicked.connect(self._set_to_center)
        self.retranslate(language)

    def minimumSizeHint(self) -> QSize:
        return QSize(240, 260)

    def sizeHint(self) -> QSize:
        return QSize(260, 320)

    def set_context(self, context: QueryContext) -> None:
        self._context = context
        self._update_spin_bounds()
        self._set_to_ego()

    def profile_spec(self) -> ProfileSpec:
        return ProfileSpec(
            axis=str(self._axis_selector.currentData()),
            coordinate=float(self._coordinate_spin.value()),
        )

    def set_profile_result(self, result: ComparisonProfileResult | None, *, selected_channel: str) -> None:
        if result is None:
            self._line_label.setText(t(self._language, "profile.line_label.default"))
            self._baseline_widget.set_png(None, empty_text=t(self._language, "profile.no_result"))
            self._candidate_widget.set_png(None, empty_text=t(self._language, "profile.no_result"))
            self._diff_widget.set_png(None, empty_text=t(self._language, "profile.no_result"))
            self.setToolTip("")
            return
        self._line_label.setText(
            t(
                self._language,
                "profile.line_label.value",
                axis=result.spec.axis,
                coordinate_axis=result.spec.coordinate_axis,
                coordinate=result.spec.coordinate,
                selected_channel=selected_channel,
            )
        )
        try:
            from driving_preference_field.profile_inspection import profile_plot_png_bytes

            self._baseline_widget.set_png(
                profile_plot_png_bytes(result, selected_channel=selected_channel, view="baseline")
            )
            self._candidate_widget.set_png(
                profile_plot_png_bytes(result, selected_channel=selected_channel, view="candidate")
            )
            self._diff_widget.set_png(
                profile_plot_png_bytes(result, selected_channel=selected_channel, view="diff")
            )
            self.setToolTip("")
        except Exception as exc:  # pragma: no cover - exercised by UI test with monkeypatch
            LOGGER.exception("Profile preview rendering failed: %s", exc)
            message = t(self._language, "profile.preview_unavailable")
            tooltip = t(self._language, "profile.preview_tooltip", error=exc)
            self._baseline_widget.set_png(None, empty_text=message)
            self._candidate_widget.set_png(None, empty_text=message)
            self._diff_widget.set_png(None, empty_text=message)
            self.setToolTip(tooltip)

    def _on_axis_changed(self) -> None:
        self._update_spin_bounds()
        if self._context is not None:
            self._set_to_ego()
        else:
            self._emit_spec_changed()

    def _update_spin_bounds(self) -> None:
        if self._context is None:
            return
        axis = str(self._axis_selector.currentData())
        self._coordinate_spin.blockSignals(True)
        if axis == "horizontal":
            self._coordinate_spin.setRange(
                self._context.local_window.y_min,
                self._context.local_window.y_max,
            )
        else:
            self._coordinate_spin.setRange(
                self._context.local_window.x_min,
                self._context.local_window.x_max,
            )
        self._coordinate_spin.blockSignals(False)

    def _set_to_ego(self) -> None:
        if self._context is None:
            return
        axis = str(self._axis_selector.currentData())
        coordinate = self._context.ego_pose.y if axis == "horizontal" else self._context.ego_pose.x
        self._set_coordinate(coordinate)

    def _set_to_center(self) -> None:
        if self._context is None:
            return
        axis = str(self._axis_selector.currentData())
        if axis == "horizontal":
            coordinate = 0.5 * (self._context.local_window.y_min + self._context.local_window.y_max)
        else:
            coordinate = 0.5 * (self._context.local_window.x_min + self._context.local_window.x_max)
        self._set_coordinate(coordinate)

    def _set_coordinate(self, coordinate: float) -> None:
        self._coordinate_spin.blockSignals(True)
        self._coordinate_spin.setValue(coordinate)
        self._coordinate_spin.blockSignals(False)
        self._emit_spec_changed()

    def _emit_spec_changed(self) -> None:
        self.profileSpecChanged.emit(str(self._axis_selector.currentData()), float(self._coordinate_spin.value()))

    def retranslate(self, language: str) -> None:
        self._language = language
        current_axis = str(self._axis_selector.currentData()) if self._axis_selector.count() else "horizontal"
        self._axis_selector.blockSignals(True)
        self._axis_selector.clear()
        self._axis_selector.addItem(t(language, "profile.axis.horizontal"), "horizontal")
        self._axis_selector.addItem(t(language, "profile.axis.vertical"), "vertical")
        index = self._axis_selector.findData(current_axis)
        self._axis_selector.setCurrentIndex(index if index >= 0 else 0)
        self._axis_selector.blockSignals(False)
        self._ego_button.setText(t(language, "profile.use_ego"))
        self._center_button.setText(t(language, "profile.use_center"))
        self._line_control_label.setText(t(language, "profile.line"))
        self._coord_control_label.setText(t(language, "profile.coord"))
        self._tabs.setTabText(0, t(language, "tab.baseline"))
        self._tabs.setTabText(1, t(language, "tab.candidate"))
        self._tabs.setTabText(2, t(language, "tab.diff"))
        self._baseline_widget.retranslate(language)
        self._candidate_widget.retranslate(language)
        self._diff_widget.retranslate(language)
        if not self.toolTip():
            self._line_label.setText(t(language, "profile.line_label.default"))
