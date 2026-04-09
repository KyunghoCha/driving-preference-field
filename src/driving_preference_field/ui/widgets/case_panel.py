from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from driving_preference_field.contracts import QueryContext, QueryWindow, StateSample


CONTROL_LABELS = {
    "ego_x": "ego x",
    "ego_y": "ego y",
    "ego_yaw": "ego yaw",
    "window_x_min": "x min",
    "window_x_max": "x max",
    "window_y_min": "y min",
    "window_y_max": "y max",
}


class CasePanelWidget(QWidget):
    caseChanged = pyqtSignal(str)
    caseControlsApplied = pyqtSignal(object, object)
    caseControlsReset = pyqtSignal()

    def __init__(self, cases_root: Path) -> None:
        super().__init__()
        self._cases_root = cases_root
        self._default_context: QueryContext | None = None
        self._applied_ego_pose: StateSample | None = None
        self._applied_local_window: QueryWindow | None = None
        self._combo = QComboBox()
        self._combo.currentIndexChanged.connect(self._emit_case)

        self._controls: dict[str, QDoubleSpinBox] = {}
        self._apply_button = QPushButton("Apply Case")
        self._reset_button = QPushButton("Reset Case")
        self._apply_button.setEnabled(False)
        self._apply_button.clicked.connect(self._apply_controls)
        self._reset_button.clicked.connect(self._reset_controls)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        form.addRow("case", self._combo)

        control_specs = (
            ("ego_x", -1000.0, 1000.0),
            ("ego_y", -1000.0, 1000.0),
            ("ego_yaw", -6.2832, 6.2832),
            ("window_x_min", -1000.0, 1000.0),
            ("window_x_max", -1000.0, 1000.0),
            ("window_y_min", -1000.0, 1000.0),
            ("window_y_max", -1000.0, 1000.0),
        )
        for key, minimum, maximum in control_specs:
            spin = QDoubleSpinBox()
            spin.setDecimals(4)
            spin.setRange(minimum, maximum)
            spin.setSingleStep(0.1)
            spin.valueChanged.connect(self._on_control_changed)
            self._controls[key] = spin
            form.addRow(CONTROL_LABELS[key], spin)

        layout.addWidget(self._apply_button)
        layout.addWidget(self._reset_button)
        layout.addStretch(1)
        self.reload_cases()

    def reload_cases(self) -> None:
        current = self.current_case_path()
        self._combo.blockSignals(True)
        self._combo.clear()
        for case_path in sorted(self._cases_root.glob("*.yaml")):
            self._combo.addItem(case_path.stem, str(case_path))
        if current is not None:
            index = self._combo.findData(current)
            if index >= 0:
                self._combo.setCurrentIndex(index)
        self._combo.blockSignals(False)

    def current_case_path(self) -> str | None:
        value = self._combo.currentData()
        return str(value) if value else None

    def set_case_path(self, case_path: Path | str) -> None:
        normalized = self._normalize_case_path(case_path)
        index = self._combo.findData(normalized)
        if index >= 0:
            self._combo.setCurrentIndex(index)

    def _normalize_case_path(self, case_path: Path | str) -> str:
        candidate = Path(case_path)
        if candidate.is_absolute():
            return str(candidate.resolve())
        direct = (self._cases_root / candidate).resolve()
        if direct.exists():
            return str(direct)
        return str(candidate.resolve())

    def set_context_values(self, *, default_context: QueryContext, working_context: QueryContext) -> None:
        self._default_context = default_context
        self._applied_ego_pose = working_context.ego_pose
        self._applied_local_window = working_context.local_window
        values = {
            "ego_x": working_context.ego_pose.x,
            "ego_y": working_context.ego_pose.y,
            "ego_yaw": working_context.ego_pose.yaw,
            "window_x_min": working_context.local_window.x_min,
            "window_x_max": working_context.local_window.x_max,
            "window_y_min": working_context.local_window.y_min,
            "window_y_max": working_context.local_window.y_max,
        }
        for key, value in values.items():
            control = self._controls[key]
            control.blockSignals(True)
            control.setValue(float(value))
            control.blockSignals(False)
        self._apply_button.setEnabled(False)

    def _emit_case(self) -> None:
        value = self.current_case_path()
        if value:
            self.caseChanged.emit(value)

    def _on_control_changed(self) -> None:
        if self._applied_ego_pose is None or self._applied_local_window is None:
            self._apply_button.setEnabled(False)
            return
        pending_ego_pose, pending_local_window = self._pending_values()
        changed = (
            pending_ego_pose != self._applied_ego_pose
            or pending_local_window != self._applied_local_window
        )
        self._apply_button.setEnabled(changed)

    def _pending_values(self) -> tuple[StateSample, QueryWindow]:
        ego_pose = StateSample(
            x=self._controls["ego_x"].value(),
            y=self._controls["ego_y"].value(),
            yaw=self._controls["ego_yaw"].value(),
        )
        local_window = QueryWindow(
            x_min=self._controls["window_x_min"].value(),
            x_max=self._controls["window_x_max"].value(),
            y_min=self._controls["window_y_min"].value(),
            y_max=self._controls["window_y_max"].value(),
        )
        return ego_pose, local_window

    def _apply_controls(self) -> None:
        ego_pose, local_window = self._pending_values()
        self._applied_ego_pose = ego_pose
        self._applied_local_window = local_window
        self._apply_button.setEnabled(False)
        self.caseControlsApplied.emit(ego_pose, local_window)

    def _reset_controls(self) -> None:
        if self._default_context is None:
            return
        self.set_context_values(
            default_context=self._default_context,
            working_context=self._default_context,
        )
        self.caseControlsReset.emit()
