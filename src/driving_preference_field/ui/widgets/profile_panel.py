from __future__ import annotations

import logging

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
from driving_preference_field.profile_inspection import ComparisonProfileResult, ProfileSpec, profile_plot_png_bytes


LOGGER = logging.getLogger(__name__)

_PROFILE_PLOT_FAILURE_TEXT = "Profile preview unavailable.\nPlot rendering failed for this view."
_PROFILE_IMAGE_DECODE_FAILURE_TEXT = "Profile preview unavailable.\nImage decoding failed."


class _ProfileImageWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._label = QLabel("No profile result")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumSize(0, 0)
        self._label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        scroll = QScrollArea()
        scroll.setWidget(self._label)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def minimumSizeHint(self) -> QSize:
        return QSize(120, 120)

    def sizeHint(self) -> QSize:
        return QSize(220, 180)

    def set_message(self, text: str, *, details: str | None = None) -> None:
        self._label.setPixmap(QPixmap())
        self._label.setText(text)
        self._label.setToolTip(details or "")

    def set_png(self, payload: bytes | None, *, empty_text: str = "No profile result") -> None:
        if not payload:
            self.set_message(empty_text)
            return
        pixmap = QPixmap()
        if not pixmap.loadFromData(payload):
            self.set_message(_PROFILE_IMAGE_DECODE_FAILURE_TEXT)
            return
        self._label.setText("")
        self._label.setToolTip("")
        self._label.setPixmap(pixmap)
        self._label.adjustSize()


class ProfilePanelWidget(QWidget):
    profileSpecChanged = pyqtSignal(str, float)

    def __init__(self) -> None:
        super().__init__()
        self._context: QueryContext | None = None
        self._axis_selector = QComboBox()
        self._axis_selector.addItem("Horizontal (constant y)", "horizontal")
        self._axis_selector.addItem("Vertical (constant x)", "vertical")
        self._coordinate_spin = QDoubleSpinBox()
        self._coordinate_spin.setDecimals(3)
        self._coordinate_spin.setSingleStep(0.1)
        self._ego_button = QPushButton("Use Ego")
        self._center_button = QPushButton("Use Center")
        self._line_label = QLabel("Line")
        self._line_label.setWordWrap(True)
        self._line_label.setMinimumWidth(0)
        self._line_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self._tabs = QTabWidget()
        self._baseline_widget = _ProfileImageWidget()
        self._candidate_widget = _ProfileImageWidget()
        self._diff_widget = _ProfileImageWidget()
        self._tabs.addTab(self._baseline_widget, "Baseline")
        self._tabs.addTab(self._candidate_widget, "Candidate")
        self._tabs.addTab(self._diff_widget, "Diff")

        controls = QGridLayout()
        controls.addWidget(QLabel("line"), 0, 0)
        controls.addWidget(self._axis_selector, 0, 1)
        controls.addWidget(QLabel("coord"), 1, 0)
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

    def set_context(self, context: QueryContext) -> None:
        self._context = context
        self._update_spin_bounds()
        self._set_to_ego()

    def profile_spec(self) -> ProfileSpec:
        return ProfileSpec(
            axis=str(self._axis_selector.currentData()),
            coordinate=float(self._coordinate_spin.value()),
        )

    def _set_profile_view(
        self,
        target: _ProfileImageWidget,
        *,
        result: ComparisonProfileResult,
        selected_channel: str,
        view: str,
    ) -> None:
        try:
            payload = profile_plot_png_bytes(result, selected_channel=selected_channel, view=view)
        except Exception as exc:
            LOGGER.exception("Failed to render profile preview for %s view", view)
            details = f"{type(exc).__name__}: {exc}"
            target.set_message(_PROFILE_PLOT_FAILURE_TEXT, details=details)
            return
        target.set_png(payload)

    def set_profile_result(self, result: ComparisonProfileResult | None, *, selected_channel: str) -> None:
        if result is None:
            self._line_label.setText("Line")
            self._baseline_widget.set_png(None)
            self._candidate_widget.set_png(None)
            self._diff_widget.set_png(None)
            return
        self._line_label.setText(
            f"{result.spec.axis} line | {result.spec.coordinate_axis}={result.spec.coordinate:.3f} | selected={selected_channel}"
        )
        self._set_profile_view(
            self._baseline_widget,
            result=result,
            selected_channel=selected_channel,
            view="baseline",
        )
        self._set_profile_view(
            self._candidate_widget,
            result=result,
            selected_channel=selected_channel,
            view="candidate",
        )
        self._set_profile_view(
            self._diff_widget,
            result=result,
            selected_channel=selected_channel,
            view="diff",
        )

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
