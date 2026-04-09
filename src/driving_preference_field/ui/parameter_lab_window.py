from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QToolButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from driving_preference_field.comparison_session import ComparisonSession
from driving_preference_field.config import (
    ComparisonPreset,
    DEFAULT_FIELD_CONFIG,
    FieldConfig,
    progression_family_label,
)
from driving_preference_field.contracts import QueryContext, QueryWindow, StateSample
from driving_preference_field.profile_inspection import (
    ComparisonProfileResult,
    build_comparison_profile,
    export_profile_bundle,
    summarize_profile_result,
)
from driving_preference_field.presets import (
    DEFAULT_PRESET_DIR,
    can_overwrite_preset,
    default_preset_path,
    indexed_presets,
    load_preset,
    save_preset,
)
from driving_preference_field.rendering import render_case, render_diff_image, summarize_diff_array
from driving_preference_field.toy_loader import load_toy_snapshot
from driving_preference_field.ui.async_raster_evaluator import AsyncRasterEvaluator, RasterComparisonResult
from driving_preference_field.ui.canvas_view import RasterCanvasView, raster_to_qimage
from driving_preference_field.ui.parameter_guide import parameter_help_html
from driving_preference_field.ui.widgets.case_panel import CasePanelWidget
from driving_preference_field.ui.widgets.color_scale_widget import ColorScaleWidget
from driving_preference_field.ui.widgets.layer_panel import LayerPanelWidget
from driving_preference_field.ui.widgets.preset_panel import PresetPanelWidget
from driving_preference_field.ui.widgets.progression_parameter_panel import ProgressionParameterPanelWidget
from driving_preference_field.ui.widgets.profile_panel import ProfilePanelWidget
from driving_preference_field.ui.widgets.summary_panel import SummaryPanelWidget
from driving_preference_field.ui.widgets.text_viewer_dialog import TextViewerDialog
from driving_preference_field.visualization_scale import (
    SCALE_MODE_FIXED,
    SCALE_MODE_NORMALIZED,
    display_unit,
    format_display_range,
    resolve_display_range,
)


CHANNEL_OPTIONS = {
    "progression_tilted": ("Progression Tilted", "plasma"),
    "progression_s_hat": ("Progression s_hat", "viridis"),
    "progression_n_hat": ("Progression n_hat", "magma"),
    "progression_longitudinal_component": ("Longitudinal Component", "plasma"),
    "progression_transverse_component": ("Transverse Component", "cividis"),
    "progression_support_mod": ("Support Modulation", "inferno"),
    "progression_alignment_mod": ("Alignment Modulation", "inferno"),
    "interior_boundary": ("Interior Boundary", "magma"),
    "continuity_branch": ("Continuity Branch", "cividis"),
    "base_preference_total": ("Base Preference Total", "viridis"),
    "safety_soft": ("Safety Soft Burden", "inferno"),
}

COMPARE_LAYOUT_OPTIONS = {
    "stacked": ("Stacked", Qt.Orientation.Vertical),
    "side_by_side": ("Side-by-side", Qt.Orientation.Horizontal),
}

SCALE_MODE_OPTIONS = {
    SCALE_MODE_FIXED: "Fixed",
    SCALE_MODE_NORMALIZED: "Normalized",
}

PARAMETER_HELP_TEXT = parameter_help_html()


@dataclass
class _PresetSideState:
    preset_name: str
    note: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    source_path: Path | None = None
    unsaved: bool = False

    def display_name(self) -> str:
        return f"{self.preset_name} (unsaved)" if self.unsaved else self.preset_name

    def to_preset(self, config: FieldConfig, *, side: str) -> ComparisonPreset:
        metadata = dict(self.metadata)
        metadata["role"] = side
        metadata.setdefault("label", self.preset_name)
        metadata.setdefault("family", progression_family_label(config.progression))
        metadata["origin"] = "user" if self.unsaved else str(metadata.get("origin", "user"))
        metadata["unsaved"] = self.unsaved
        return ComparisonPreset(
            preset_name=self.preset_name,
            field_config=config,
            note=self.note,
            metadata=metadata,
        )


class CompareTabWidget(QWidget):
    def __init__(self, splitter: QSplitter, button: QToolButton) -> None:
        super().__init__()
        self._button = button
        self._button.setParent(self)
        self._button.show()
        self._button.raise_()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        size = self._button.sizeHint()
        right_margin = 6
        top_margin = 4
        self._button.move(self.width() - size.width() - right_margin, top_margin)
        self._button.raise_()


class ViewPaneWidget(QWidget):
    def __init__(self, title: str, view: RasterCanvasView, *, show_title: bool = True) -> None:
        super().__init__()
        self._title_label = QLabel(title)
        self._title_label.setVisible(show_title)
        self._scale_widget = ColorScaleWidget()

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)
        content_layout.addWidget(view, 1)
        content_layout.addWidget(self._scale_widget, 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        layout.addWidget(self._title_label)
        layout.addLayout(content_layout, 1)

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)

    def set_scale_info(
        self,
        *,
        cmap_name: str,
        value_range: tuple[float, float],
        diff: bool,
    ) -> None:
        self._scale_widget.set_scale(cmap_name=cmap_name, value_range=value_range, diff=diff)


class ParameterLabWindow(QMainWindow):
    def __init__(
        self,
        *,
        case_path: Path | None = None,
        baseline_preset: Path | None = None,
        candidate_preset: Path | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("driving-preference-field | Parameter Lab")
        self.resize(1600, 950)
        self.setMinimumSize(1280, 760)

        self._repo_root = Path(__file__).resolve().parents[3]
        self._cases_root = self._repo_root / "cases/toy"
        self._preset_root = self._repo_root / DEFAULT_PRESET_DIR
        self._preset_root.mkdir(parents=True, exist_ok=True)

        self._selected_channel = "progression_tilted"
        self._scale_mode = SCALE_MODE_FIXED
        self._compare_layout = "stacked"
        self._single_side = "baseline"
        self._qualitative_note = ""
        self._baseline_state = _PresetSideState(preset_name="baseline_default")
        self._candidate_state = _PresetSideState(preset_name="candidate_default")
        self._baseline_config = DEFAULT_FIELD_CONFIG
        self._candidate_config = DEFAULT_FIELD_CONFIG
        self._initialize_side_from_path("baseline", Path(baseline_preset) if baseline_preset else None)
        self._initialize_side_from_path("candidate", Path(candidate_preset) if candidate_preset else None)

        case_candidates = sorted(self._cases_root.glob("*.yaml"))
        if not case_candidates and case_path is None:
            raise RuntimeError(f"no toy cases found under {self._cases_root}")
        initial_case = self._normalize_case_path(Path(case_path) if case_path is not None else case_candidates[0])
        self._snapshot, loaded_context = load_toy_snapshot(initial_case)
        self._current_case_path = initial_case
        self._default_context = loaded_context
        self._working_context = loaded_context
        self._comparison_result: RasterComparisonResult | None = None
        self._profile_result: ComparisonProfileResult | None = None
        self._reset_views_pending = True

        self._async = AsyncRasterEvaluator(debounce_ms=100)
        self._status_label = QLabel("idle")
        self._hover_label = QLabel("(x, y)=(-,-)")

        self._case_panel = CasePanelWidget(self._cases_root)
        self._layer_panel = LayerPanelWidget()
        self._baseline_panel = ProgressionParameterPanelWidget(title="Baseline Progression")
        self._candidate_panel = ProgressionParameterPanelWidget(title="Candidate Progression")
        self._preset_panel = PresetPanelWidget()
        self._summary_panel = SummaryPanelWidget()
        self._profile_panel = ProfilePanelWidget()

        self._baseline_view = RasterCanvasView()
        self._candidate_view = RasterCanvasView()
        self._diff_view = RasterCanvasView()
        self._single_view = RasterCanvasView()
        self._baseline_pane = ViewPaneWidget("Baseline", self._baseline_view)
        self._candidate_pane = ViewPaneWidget("Candidate", self._candidate_view)
        self._diff_pane = ViewPaneWidget("Diff", self._diff_view, show_title=False)
        self._single_pane = ViewPaneWidget("Baseline", self._single_view, show_title=False)
        self._single_selector = QComboBox()
        self._single_selector.addItems(["baseline", "candidate"])

        self._channel_selector = QComboBox()
        for channel_name, (label, _) in CHANNEL_OPTIONS.items():
            self._channel_selector.addItem(label, channel_name)
        self._channel_selector.setCurrentIndex(self._channel_selector.findData(self._selected_channel))
        self._scale_selector = QComboBox()
        for scale_mode, label in SCALE_MODE_OPTIONS.items():
            self._scale_selector.addItem(label, scale_mode)
        self._scale_selector.setCurrentIndex(self._scale_selector.findData(self._scale_mode))
        self._scale_info_label = QLabel()
        self._compare_layout_button = QToolButton()
        self._compare_layout_button.setAutoRaise(True)
        self._compare_layout_button.setFixedSize(22, 20)
        self._compare_layout_button.setStyleSheet(
            "QToolButton {"
            "background: rgba(255, 255, 255, 0.88);"
            "border: 1px solid rgba(0, 0, 0, 0.18);"
            "border-radius: 3px;"
            "padding: 0px 2px;"
            "font-size: 10px;"
            "}"
        )
        self._update_compare_layout_button()
        self._parameter_help_dialog: TextViewerDialog | None = None

        self._build_ui()
        self._wire_signals()
        self._baseline_panel.set_config(self._baseline_config)
        self._candidate_panel.set_config(self._candidate_config)
        self._profile_panel.set_context(self._working_context)
        self._case_panel.set_context_values(
            default_context=self._default_context,
            working_context=self._working_context,
        )
        self._case_panel.set_case_path(initial_case)
        self._refresh_preset_list()
        self._apply_layer_visibility()
        self._schedule_evaluation()

    def closeEvent(self, event) -> None:
        self._async.shutdown()
        super().closeEvent(event)

    def export_current_comparison(self) -> Path | None:
        if self._comparison_result is None:
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_root = self._repo_root / "artifacts/lab_exports" / self._current_case_path.stem / timestamp
        baseline_dir = export_root / "baseline"
        candidate_dir = export_root / "candidate"
        baseline_artifacts = render_case(
            self._snapshot,
            self._working_context,
            case_name=self._current_case_path.stem,
            config=self._baseline_config,
            out_dir=baseline_dir,
            scale_mode=self._scale_mode,
        )
        candidate_artifacts = render_case(
            self._snapshot,
            self._working_context,
            case_name=self._current_case_path.stem,
            config=self._candidate_config,
            out_dir=candidate_dir,
            scale_mode=self._scale_mode,
        )
        diff_data = self._selected_diff_array()
        render_diff_image(
            diff_data,
            (
                self._working_context.local_window.x_min,
                self._working_context.local_window.x_max,
                self._working_context.local_window.y_min,
                self._working_context.local_window.y_max,
            ),
            channel_name=self._selected_channel,
            title=f"Diff [{self._selected_channel}]",
            out_path=export_root / f"diff_{self._selected_channel}.png",
            scale_mode=self._scale_mode,
        )
        save_preset(
            self._current_baseline_preset(),
            export_root / "baseline_preset.yaml",
        )
        save_preset(
            self._current_candidate_preset(),
            export_root / "candidate_preset.yaml",
        )
        profile_payload = {"available": False, "selected_channel": self._selected_channel}
        profile_result = self._current_profile_result()
        if profile_result is not None:
            profile_payload = export_profile_bundle(
                profile_result,
                selected_channel=self._selected_channel,
                out_dir=export_root / "profile",
            )
        session = self._build_comparison_session(
            baseline_render_summary=baseline_artifacts.summary,
            candidate_render_summary=candidate_artifacts.summary,
            profile_summary=profile_payload,
            exported_at=timestamp,
        )
        (export_root / "comparison_session.json").write_text(
            json.dumps(session.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return export_root

    def _build_ui(self) -> None:
        self._build_toolbar()
        self._build_central_tabs()
        self._case_dock = self._add_dock("Case Controls", self._case_panel, Qt.DockWidgetArea.LeftDockWidgetArea)
        self._left_tabs = QTabWidget()
        self._left_tabs.addTab(self._preset_panel, "Presets")
        self._left_tabs.addTab(self._summary_panel, "Summary")
        self._left_tabs.addTab(self._profile_panel, "Profile")
        self._left_tabs.addTab(self._layer_panel, "Layers")
        self._left_tabs.setDocumentMode(True)
        self._left_stack_dock = self._add_dock("Workspace", self._left_tabs, Qt.DockWidgetArea.LeftDockWidgetArea)

        self._parameter_tabs = QTabWidget()
        self._parameter_tabs.addTab(self._wrap_scroll(self._baseline_panel), "Baseline")
        self._parameter_tabs.addTab(self._wrap_scroll(self._candidate_panel), "Candidate")
        self._parameter_tabs.setDocumentMode(True)
        self._parameter_dock = self._add_dock("Parameters", self._parameter_tabs, Qt.DockWidgetArea.RightDockWidgetArea)

        self._case_dock.setMinimumWidth(0)
        self._left_stack_dock.setMinimumWidth(0)
        self._parameter_dock.setMinimumWidth(320)
        self.splitDockWidget(self._case_dock, self._left_stack_dock, Qt.Orientation.Vertical)
        self.resizeDocks([self._case_dock, self._left_stack_dock], [330, 400], Qt.Orientation.Vertical)
        self.statusBar().addPermanentWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._hover_label, 2)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Parameter Lab")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        reload_action = QAction("Reload Case", self)
        reset_action = QAction("Reset View", self)
        export_action = QAction("Export Comparison", self)
        reload_action.triggered.connect(self._reload_case)
        reset_action.triggered.connect(self._reset_views)
        export_action.triggered.connect(self._export_comparison)
        toolbar.addAction(reload_action)
        toolbar.addAction(reset_action)
        toolbar.addAction(export_action)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("channel"))
        toolbar.addWidget(self._channel_selector)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("scale"))
        toolbar.addWidget(self._scale_selector)
        toolbar.addWidget(self._scale_info_label)

    def _build_central_tabs(self) -> None:
        self._tabs = QTabWidget()

        self._compare_splitter = QSplitter(COMPARE_LAYOUT_OPTIONS[self._compare_layout][1])
        self._compare_splitter.addWidget(self._baseline_pane)
        self._compare_splitter.addWidget(self._candidate_pane)
        self._compare_splitter.setSizes([1, 1])
        compare_container = CompareTabWidget(self._compare_splitter, self._compare_layout_button)

        single_container = QWidget()
        single_layout = QVBoxLayout(single_container)
        single_layout.addWidget(self._single_selector)
        single_layout.addWidget(self._single_pane)
        self._tabs.addTab(single_container, "Single")
        self._tabs.addTab(compare_container, "Compare")
        self._tabs.addTab(self._diff_pane, "Diff")

        self.setCentralWidget(self._tabs)

    def _wrap_scroll(self, widget: QWidget) -> QScrollArea:
        area = QScrollArea()
        area.setWidget(widget)
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        return area

    def _add_dock(self, title: str, widget: QWidget, area: Qt.DockWidgetArea) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        return dock

    def _wire_signals(self) -> None:
        self._case_panel.caseChanged.connect(self._on_case_changed)
        self._case_panel.caseControlsApplied.connect(self._on_case_controls_applied)
        self._case_panel.caseControlsReset.connect(self._on_case_controls_reset)
        self._layer_panel.visibilityChanged.connect(lambda *_: self._apply_layer_visibility())
        self._baseline_panel.configApplied.connect(self._on_baseline_config_changed)
        self._candidate_panel.configApplied.connect(self._on_candidate_config_changed)
        self._baseline_panel.helpRequested.connect(self._show_parameter_help)
        self._candidate_panel.helpRequested.connect(self._show_parameter_help)
        self._preset_panel.loadRequested.connect(self._load_preset_into_side)
        self._preset_panel.saveRequested.connect(self._save_preset_from_side)
        self._preset_panel.copyRequested.connect(self._copy_side)
        self._channel_selector.currentIndexChanged.connect(self._on_channel_changed)
        self._scale_selector.currentIndexChanged.connect(self._on_scale_mode_changed)
        self._compare_layout_button.clicked.connect(self._toggle_compare_layout)
        self._single_selector.currentTextChanged.connect(self._on_single_side_changed)
        self._profile_panel.profileSpecChanged.connect(self._on_profile_spec_changed)
        self._tabs.currentChanged.connect(lambda *_: self._refresh_scale_info_label())
        self._summary_panel.noteChanged.connect(self._on_note_changed)
        for view in (self._baseline_view, self._candidate_view, self._diff_view, self._single_view):
            view.hoverChanged.connect(self._update_hover)
        self._async.comparisonReady.connect(self._on_comparison_ready)
        self._async.evaluationFailed.connect(self._on_evaluation_failed)
        self._async.busyChanged.connect(self._on_busy_changed)

    def _initialize_side_from_path(self, side: str, preset_path: Path | None) -> None:
        resolved_path = preset_path
        if resolved_path is None or not resolved_path.exists():
            resolved_path = default_preset_path(side, self._preset_root)
        if resolved_path is None or not resolved_path.exists():
            return
        preset = load_preset(resolved_path)
        self._set_side_from_preset(side, preset, source_path=resolved_path, unsaved=False, schedule=False)

    def _normalize_case_path(self, case_path: Path | str) -> Path:
        candidate = Path(case_path)
        if candidate.is_absolute():
            return candidate.resolve()
        repo_relative = (self._repo_root / candidate).resolve()
        if repo_relative.exists():
            return repo_relative
        cases_relative = (self._cases_root / candidate).resolve()
        if cases_relative.exists():
            return cases_relative
        return candidate.resolve()

    def _set_side_from_preset(
        self,
        side: str,
        preset: ComparisonPreset,
        *,
        source_path: Path | None,
        unsaved: bool,
        schedule: bool = True,
    ) -> None:
        state = _PresetSideState(
            preset_name=preset.preset_name,
            note=preset.note,
            metadata=dict(preset.metadata),
            source_path=source_path,
            unsaved=unsaved,
        )
        if side == "baseline":
            self._baseline_state = state
            self._baseline_config = preset.field_config
            if hasattr(self, "_baseline_panel"):
                self._baseline_panel.set_config(self._baseline_config)
        else:
            self._candidate_state = state
            self._candidate_config = preset.field_config
            if hasattr(self, "_candidate_panel"):
                self._candidate_panel.set_config(self._candidate_config)
        if schedule:
            self._schedule_evaluation()

    def _mark_side_unsaved(self, side: str) -> None:
        state = self._baseline_state if side == "baseline" else self._candidate_state
        metadata = dict(state.metadata)
        metadata["role"] = side
        metadata["origin"] = "user"
        metadata.setdefault("label", state.preset_name)
        updated = _PresetSideState(
            preset_name=state.preset_name,
            note=state.note,
            metadata=metadata,
            source_path=state.source_path,
            unsaved=True,
        )
        if side == "baseline":
            self._baseline_state = updated
        else:
            self._candidate_state = updated

    def _refresh_preset_list(self) -> None:
        descriptors = indexed_presets(self._preset_root)
        baseline_descriptors = [descriptor for descriptor in descriptors if descriptor.role in (None, "baseline")]
        candidate_descriptors = [descriptor for descriptor in descriptors if descriptor.role in (None, "candidate")]
        self._preset_panel.set_presets(
            baseline_presets=baseline_descriptors,
            candidate_presets=candidate_descriptors,
        )

    def _reload_case(self) -> None:
        self._snapshot, loaded_context = load_toy_snapshot(self._current_case_path)
        self._default_context = loaded_context
        self._working_context = loaded_context
        self._profile_panel.set_context(self._working_context)
        self._profile_result = None
        self._reset_views_pending = True
        self._qualitative_note = ""
        self._summary_panel.set_note("")
        self._case_panel.set_context_values(
            default_context=self._default_context,
            working_context=self._working_context,
        )
        self._schedule_evaluation()

    def _reset_views(self) -> None:
        for view in (self._baseline_view, self._candidate_view, self._diff_view, self._single_view):
            view.reset_view()

    def _apply_layer_visibility(self) -> None:
        visibility = self._layer_panel.visibility()
        for view in (self._baseline_view, self._candidate_view, self._diff_view, self._single_view):
            view.set_overlay_visibility(visibility)

    def _schedule_evaluation(self) -> None:
        self._async.request(
            self._snapshot,
            self._working_context,
            baseline_config=self._baseline_config,
            candidate_config=self._candidate_config,
            x_samples=160,
            y_samples=160,
        )

    def _on_case_changed(self, case_path: str) -> None:
        self._current_case_path = self._normalize_case_path(case_path)
        self._snapshot, loaded_context = load_toy_snapshot(self._current_case_path)
        self._default_context = loaded_context
        self._working_context = loaded_context
        self._profile_panel.set_context(self._working_context)
        self._profile_result = None
        self._reset_views_pending = True
        self._qualitative_note = ""
        self._summary_panel.set_note("")
        self._case_panel.set_context_values(
            default_context=self._default_context,
            working_context=self._working_context,
        )
        self._schedule_evaluation()

    def _on_case_controls_applied(self, ego_pose: StateSample, local_window: QueryWindow) -> None:
        self._working_context = QueryContext(
            semantic_snapshot=self._snapshot,
            ego_pose=ego_pose,
            local_window=local_window,
            mode=self._default_context.mode,
            phase=self._default_context.phase,
        )
        self._profile_panel.set_context(self._working_context)
        self._profile_result = None
        self._reset_views_pending = True
        self._schedule_evaluation()

    def _on_case_controls_reset(self) -> None:
        self._working_context = self._default_context
        self._profile_panel.set_context(self._working_context)
        self._profile_result = None
        self._reset_views_pending = True
        self._schedule_evaluation()

    def _on_baseline_config_changed(self, config: FieldConfig) -> None:
        self._baseline_config = config
        self._mark_side_unsaved("baseline")
        self._schedule_evaluation()

    def _on_candidate_config_changed(self, config: FieldConfig) -> None:
        self._candidate_config = config
        self._mark_side_unsaved("candidate")
        self._schedule_evaluation()

    def _load_preset_into_side(self, side: str, preset_path: str) -> None:
        preset = load_preset(preset_path)
        self._set_side_from_preset(side, preset, source_path=Path(preset_path), unsaved=False)

    def _save_preset_from_side(self, side: str, preset_name: str) -> None:
        config = self._baseline_config if side == "baseline" else self._candidate_config
        current_state = self._baseline_state if side == "baseline" else self._candidate_state
        target_path = self._preset_root / f"{preset_name}.yaml"
        allowed, message = can_overwrite_preset(target_path)
        if not allowed:
            QMessageBox.warning(self, "Preset Save Rejected", message or "preset 저장이 거부되었습니다.")
            return
        metadata = dict(current_state.metadata)
        metadata.update(
            {
                "role": side,
                "origin": "user",
                "label": preset_name,
                "family": progression_family_label(config.progression),
            }
        )
        metadata.setdefault("description", f"user saved {side} preset")
        metadata.setdefault("recommended_cases", [])
        preset = ComparisonPreset(
            preset_name=preset_name,
            field_config=config,
            note=current_state.note,
            metadata=metadata,
        )
        save_preset(preset, target_path)
        self._set_side_from_preset(side, preset, source_path=target_path, unsaved=False, schedule=False)
        self._refresh_preset_list()
        self._refresh_summary()

    def _copy_side(self, source: str, target: str) -> None:
        source_config = self._baseline_config if source == "baseline" else self._candidate_config
        source_state = self._baseline_state if source == "baseline" else self._candidate_state
        metadata = dict(source_state.metadata)
        metadata["role"] = target
        metadata["origin"] = "user"
        metadata["label"] = source_state.preset_name
        metadata["description"] = f"copied from {source}"
        preset = ComparisonPreset(
            preset_name=source_state.preset_name,
            field_config=source_config,
            note=source_state.note,
            metadata=metadata,
        )
        self._set_side_from_preset(target, preset, source_path=None, unsaved=True)

    def _on_channel_changed(self) -> None:
        self._selected_channel = str(self._channel_selector.currentData())
        self._refresh_views()
        self._refresh_profile_panel()
        self._refresh_summary()

    def _on_scale_mode_changed(self) -> None:
        self._scale_mode = str(self._scale_selector.currentData())
        self._refresh_views()
        self._refresh_summary()

    def _toggle_compare_layout(self) -> None:
        self._compare_layout = (
            "side_by_side" if self._compare_layout == "stacked" else "stacked"
        )
        _, orientation = COMPARE_LAYOUT_OPTIONS[self._compare_layout]
        self._compare_splitter.setOrientation(orientation)
        self._compare_splitter.setSizes([1, 1])
        self._update_compare_layout_button()

    def _update_compare_layout_button(self) -> None:
        if self._compare_layout == "stacked":
            self._compare_layout_button.setText("↔")
            self._compare_layout_button.setToolTip("Switch compare layout to side-by-side")
        else:
            self._compare_layout_button.setText("↕")
            self._compare_layout_button.setToolTip("Switch compare layout to stacked")

    def _on_single_side_changed(self, value: str) -> None:
        self._single_side = value
        self._single_pane.set_title("Baseline" if value == "baseline" else "Candidate")
        self._refresh_views()

    def _on_note_changed(self, value: str) -> None:
        self._qualitative_note = value

    def _on_comparison_ready(self, _generation: int, result: RasterComparisonResult) -> None:
        self._comparison_result = result
        self._refresh_views()
        self._refresh_profile_panel()
        if self._reset_views_pending:
            self._reset_views()
            self._reset_views_pending = False
        self._refresh_summary()

    def _on_evaluation_failed(self, _generation: int, message: str) -> None:
        QMessageBox.critical(self, "Evaluation Failed", message)

    def _on_busy_changed(self, busy: bool) -> None:
        self._status_label.setText("computing" if busy else "idle")

    def _on_profile_spec_changed(self, _axis: str, _coordinate: float) -> None:
        self._refresh_profile_panel()
        self._refresh_summary()

    def _update_hover(self, x: float, y: float) -> None:
        self._hover_label.setText(f"(x, y)=({x:.3f}, {y:.3f})")

    def _display_range(self, data, *, diff: bool) -> tuple[float, float]:
        return resolve_display_range(
            data,
            channel_name=self._selected_channel,
            scale_mode=self._scale_mode,
            diff=diff,
        )

    def _refresh_scale_info_label(self) -> None:
        if self._comparison_result is None:
            self._scale_info_label.setText("")
            return
        baseline_data = self._comparison_result.baseline_raster.channels[self._selected_channel]
        candidate_data = self._comparison_result.candidate_raster.channels[self._selected_channel]
        diff_data = candidate_data - baseline_data
        current_tab = self._tabs.currentIndex()
        if current_tab == 2:
            value_range = self._display_range(diff_data, diff=True)
            text = format_display_range(
                self._selected_channel,
                scale_mode=self._scale_mode,
                value_range=value_range,
                diff=True,
            )
        else:
            if current_tab == 0 and self._single_side == "candidate":
                data = candidate_data
            else:
                data = baseline_data
            value_range = self._display_range(data, diff=False)
            text = format_display_range(
                self._selected_channel,
                scale_mode=self._scale_mode,
                value_range=value_range,
            )
        self._scale_info_label.setText(text)

    def _refresh_views(self) -> None:
        if self._comparison_result is None:
            return
        extent_window = self._working_context.local_window
        label, cmap = CHANNEL_OPTIONS[self._selected_channel]
        baseline_data = self._comparison_result.baseline_raster.channels[self._selected_channel]
        candidate_data = self._comparison_result.candidate_raster.channels[self._selected_channel]
        diff_data = candidate_data - baseline_data
        baseline_range = self._display_range(baseline_data, diff=False)
        candidate_range = self._display_range(candidate_data, diff=False)
        diff_range = self._display_range(diff_data, diff=True)

        self._baseline_view.set_scene_content(
            raster_to_qimage(baseline_data, cmap_name=cmap, value_range=baseline_range),
            window=extent_window,
            snapshot=self._snapshot,
            ego_pose=self._working_context.ego_pose,
        )
        self._candidate_view.set_scene_content(
            raster_to_qimage(candidate_data, cmap_name=cmap, value_range=candidate_range),
            window=extent_window,
            snapshot=self._snapshot,
            ego_pose=self._working_context.ego_pose,
        )
        self._diff_view.set_scene_content(
            raster_to_qimage(diff_data, cmap_name="coolwarm", symmetric=True, value_range=diff_range),
            window=extent_window,
            snapshot=self._snapshot,
            ego_pose=self._working_context.ego_pose,
        )
        single_data = baseline_data if self._single_side == "baseline" else candidate_data
        single_range = baseline_range if self._single_side == "baseline" else candidate_range
        self._single_view.set_scene_content(
            raster_to_qimage(single_data, cmap_name=cmap, value_range=single_range),
            window=extent_window,
            snapshot=self._snapshot,
            ego_pose=self._working_context.ego_pose,
        )
        self._baseline_pane.set_scale_info(
            cmap_name=cmap,
            value_range=baseline_range,
            diff=False,
        )
        self._candidate_pane.set_scale_info(
            cmap_name=cmap,
            value_range=candidate_range,
            diff=False,
        )
        self._single_pane.set_scale_info(
            cmap_name=cmap,
            value_range=single_range,
            diff=False,
        )
        self._diff_pane.set_scale_info(
            cmap_name="coolwarm",
            value_range=diff_range,
            diff=True,
        )
        self._apply_layer_visibility()
        self._refresh_scale_info_label()
        self._status_label.setText(f"idle | channel={label}")

    def _refresh_profile_panel(self) -> None:
        if self._comparison_result is None:
            self._profile_result = None
            self._profile_panel.set_profile_result(None, selected_channel=self._selected_channel)
            return
        self._profile_result = build_comparison_profile(
            self._comparison_result.baseline_raster,
            self._comparison_result.candidate_raster,
            spec=self._profile_panel.profile_spec(),
            selected_channel=self._selected_channel,
        )
        self._profile_panel.set_profile_result(self._profile_result, selected_channel=self._selected_channel)

    def _refresh_summary(self) -> None:
        if self._comparison_result is None:
            return
        baseline_state = self._comparison_result.baseline_state
        candidate_state = self._comparison_result.candidate_state
        summary = {
            "case": str(self._current_case_path),
            "selected_channel": self._selected_channel,
            "selected_channel_unit": display_unit(self._selected_channel),
            "scale_mode": self._scale_mode,
            "score_sign": "higher is better",
            "diff_meaning": "candidate - baseline",
            "progression_surface_kind": "whole-fabric blended coordinate field",
            "raster_role": "visualization only",
            **self._effective_context_payload(),
            "baseline_preset_name": self._baseline_state.preset_name,
            "baseline_preset_display": self._baseline_state.display_name(),
            "baseline_preset_origin": self._baseline_state.metadata.get("origin", "user"),
            "baseline_preset_unsaved": self._baseline_state.unsaved,
            "baseline_longitudinal_frame": self._baseline_config.progression.longitudinal_frame,
            "candidate_preset_name": self._candidate_state.preset_name,
            "candidate_preset_display": self._candidate_state.display_name(),
            "candidate_preset_origin": self._candidate_state.metadata.get("origin", "user"),
            "candidate_preset_unsaved": self._candidate_state.unsaved,
            "candidate_longitudinal_frame": self._candidate_config.progression.longitudinal_frame,
            "baseline": self._state_summary_payload(baseline_state),
            "candidate": self._state_summary_payload(candidate_state),
            "baseline_selected_channel_value": self._state_channel_value(baseline_state, self._selected_channel),
            "candidate_selected_channel_value": self._state_channel_value(candidate_state, self._selected_channel),
            "difference": self._diff_summary_payload(baseline_state, candidate_state),
            "profile": self._profile_summary_payload(),
            "visualization": self._visualization_payload(),
            "qualitative_note": self._qualitative_note,
        }
        self._summary_panel.set_summary(summary)

    def _selected_diff_array(self):
        assert self._comparison_result is not None
        return (
            self._comparison_result.candidate_raster.channels[self._selected_channel]
            - self._comparison_result.baseline_raster.channels[self._selected_channel]
        )

    def _current_profile_result(self) -> ComparisonProfileResult | None:
        if self._comparison_result is None:
            return None
        if self._profile_result is None:
            self._refresh_profile_panel()
        return self._profile_result

    def _profile_summary_payload(self) -> dict[str, object]:
        result = self._current_profile_result()
        if result is None:
            return {
                "available": False,
                "selected_channel": self._selected_channel,
            }
        summary = summarize_profile_result(result, selected_channel=self._selected_channel)
        return {
            "available": True,
            **summary,
        }

    def _effective_context_payload(self) -> dict[str, object]:
        return {
            "effective_ego_pose": {
                "x": self._working_context.ego_pose.x,
                "y": self._working_context.ego_pose.y,
                "yaw": self._working_context.ego_pose.yaw,
            },
            "effective_local_window": {
                "x_min": self._working_context.local_window.x_min,
                "x_max": self._working_context.local_window.x_max,
                "y_min": self._working_context.local_window.y_min,
                "y_max": self._working_context.local_window.y_max,
            },
        }

    def _state_summary_payload(self, state_result) -> dict[str, float]:
        return {
            "base_total": state_result.base_preference_total,
            "soft_total": state_result.soft_exception_total,
            "hard_count": state_result.hard_violation_count,
            "selected_channel_value": self._state_channel_value(state_result, self._selected_channel),
        }

    def _diff_summary_payload(self, baseline_state, candidate_state) -> dict[str, object]:
        baseline_selected = self._state_channel_value(baseline_state, self._selected_channel)
        candidate_selected = self._state_channel_value(candidate_state, self._selected_channel)
        return {
            "selected_channel_delta": candidate_selected - baseline_selected,
            "base_total_delta": candidate_state.base_preference_total - baseline_state.base_preference_total,
            "soft_total_delta": candidate_state.soft_exception_total - baseline_state.soft_exception_total,
            "hard_count_delta": candidate_state.hard_violation_count - baseline_state.hard_violation_count,
            "diff_raster_summary": summarize_diff_array(self._selected_diff_array()),
        }

    def _visualization_payload(self) -> dict[str, object]:
        baseline_data = self._comparison_result.baseline_raster.channels[self._selected_channel]
        candidate_data = self._comparison_result.candidate_raster.channels[self._selected_channel]
        diff_data = self._selected_diff_array()
        return {
            "scale_mode": self._scale_mode,
            "score_sign": "higher is better",
            "progression_surface_kind": "whole-fabric blended coordinate field",
            "raster_role": "visualization only",
            "selected_channel_unit": display_unit(self._selected_channel),
            "diff_unit": display_unit(self._selected_channel, diff=True),
            "baseline_range": self._display_range(baseline_data, diff=False),
            "candidate_range": self._display_range(candidate_data, diff=False),
            "diff_range": self._display_range(diff_data, diff=True),
        }

    def _state_channel_value(self, state_result, channel_name: str) -> float:
        if channel_name == "base_preference_total":
            return state_result.base_preference_total
        if channel_name in state_result.base_preference_channels:
            return state_result.base_preference_channels[channel_name]
        debug_key_map = {
            "progression_s_hat": "progression_s_hat",
            "progression_n_hat": "progression_n_hat",
            "progression_longitudinal_component": "progression_longitudinal_component",
            "progression_transverse_component": "progression_transverse_component",
            "progression_support_mod": "progression_support_mod",
            "progression_alignment_mod": "progression_alignment_mod",
        }
        if channel_name in debug_key_map:
            return float(state_result.diagnostics[debug_key_map[channel_name]])
        return state_result.soft_exception_channels[channel_name]

    def _export_comparison(self) -> None:
        export_path = self.export_current_comparison()
        if export_path is None:
            return
        QMessageBox.information(self, "Export Complete", str(export_path))

    def _show_parameter_help(self) -> None:
        if self._parameter_help_dialog is None:
            self._parameter_help_dialog = TextViewerDialog(
                title="Parameter Help",
                text=PARAMETER_HELP_TEXT.strip(),
                text_format="html",
                parent=self,
            )
        self._parameter_help_dialog.show()
        self._parameter_help_dialog.raise_()
        self._parameter_help_dialog.activateWindow()

    def _current_baseline_preset(self) -> ComparisonPreset:
        return self._baseline_state.to_preset(self._baseline_config, side="baseline")

    def _current_candidate_preset(self) -> ComparisonPreset:
        return self._candidate_state.to_preset(self._candidate_config, side="candidate")

    def _build_comparison_session(
        self,
        *,
        baseline_render_summary: dict[str, object],
        candidate_render_summary: dict[str, object],
        profile_summary: dict[str, object],
        exported_at: str,
    ) -> ComparisonSession:
        assert self._comparison_result is not None
        baseline_state = self._comparison_result.baseline_state
        candidate_state = self._comparison_result.candidate_state
        return ComparisonSession(
            case_path=str(self._current_case_path),
            selected_channel=self._selected_channel,
            effective_ego_pose=self._effective_context_payload()["effective_ego_pose"],
            effective_local_window=self._effective_context_payload()["effective_local_window"],
            baseline_preset=self._current_baseline_preset(),
            candidate_preset=self._current_candidate_preset(),
            baseline_state_summary=self._state_summary_payload(baseline_state),
            candidate_state_summary=self._state_summary_payload(candidate_state),
            diff_summary={
                **self._diff_summary_payload(baseline_state, candidate_state),
                "raster": summarize_diff_array(self._selected_diff_array()),
                "visualization": self._visualization_payload(),
            },
            profile_summary=profile_summary,
            baseline_render_summary=baseline_render_summary,
            candidate_render_summary=candidate_render_summary,
            note=self._qualitative_note,
            exported_at=exported_at,
        )
