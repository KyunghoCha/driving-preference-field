from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings, Qt
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

from driving_preference_field.config import (
    FieldConfig,
)
from driving_preference_field.contracts import QueryWindow, StateSample
from driving_preference_field.presets import save_preset
from driving_preference_field.ui.async_raster_evaluator import RasterComparisonResult
from driving_preference_field.ui.canvas_view import RasterCanvasView, raster_to_qimage
from driving_preference_field.ui.locale import (
    DEFAULT_LANGUAGE,
    language_display_items,
    normalize_language,
    t,
)
from driving_preference_field.ui.parameter_lab.constants import CHANNEL_OPTIONS, COMPARE_LAYOUT_OPTIONS
from driving_preference_field.ui.parameter_lab.coordinator import ParameterLabCoordinator
from driving_preference_field.ui.parameter_lab.help_actions import ParameterLabHelpActions
from driving_preference_field.ui.parameter_lab.presenter import build_comparison_session, summary_payload
from driving_preference_field.ui.parameter_lab.state import ParameterLabState
from driving_preference_field.ui.widgets.case_panel import CasePanelWidget
from driving_preference_field.ui.widgets.color_scale_widget import ColorScaleWidget
from driving_preference_field.ui.widgets.layer_panel import LayerPanelWidget
from driving_preference_field.ui.widgets.preset_panel import PresetPanelWidget
from driving_preference_field.ui.widgets.progression_parameter_panel import ProgressionParameterPanelWidget
from driving_preference_field.ui.widgets.profile_panel import ProfilePanelWidget
from driving_preference_field.ui.widgets.summary_panel import SummaryPanelWidget
from driving_preference_field.visualization_scale import (
    SCALE_MODE_FIXED,
    SCALE_MODE_NORMALIZED,
    display_unit,
    format_display_range,
    resolve_display_range,
)

if TYPE_CHECKING:
    from driving_preference_field.profile_contracts import ComparisonProfileResult

LOGGER = logging.getLogger(__name__)


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
        self.resize(1600, 950)
        self.setMinimumSize(1280, 760)

        self._repo_root_path = Path(__file__).resolve().parents[4].resolve()
        self._settings = QSettings("driving-preference-field", "ParameterLab")
        self._language = normalize_language(str(self._settings.value("ui/language", DEFAULT_LANGUAGE)))
        self._state = ParameterLabState(
            repo_root=self._repo_root_path,
            case_path=case_path,
            baseline_preset=baseline_preset,
            candidate_preset=candidate_preset,
        )

        self._selected_channel = "progression_tilted"
        self._scale_mode = SCALE_MODE_FIXED
        self._compare_layout = "stacked"
        self._single_side = "baseline"
        self._qualitative_note = ""
        initial_case = self._current_case_path
        self._comparison_result: RasterComparisonResult | None = None
        self._profile_result: ComparisonProfileResult | None = None
        self._reset_views_pending = True
        self._busy = False

        self._coordinator = ParameterLabCoordinator(debounce_ms=100)
        self._help_actions = ParameterLabHelpActions(repo_root=self._repo_root, parent=self)
        self._status_label = QLabel()
        self._hover_label = QLabel("(x, y)=(-,-)")

        self._case_panel = CasePanelWidget(self._cases_root, language=self._language)
        self._layer_panel = LayerPanelWidget(language=self._language)
        self._baseline_panel = ProgressionParameterPanelWidget(
            title=t(self._language, "panel.baseline_progression"),
            language=self._language,
        )
        self._candidate_panel = ProgressionParameterPanelWidget(
            title=t(self._language, "panel.candidate_progression"),
            language=self._language,
        )
        self._preset_panel = PresetPanelWidget(language=self._language)
        self._summary_panel = SummaryPanelWidget(language=self._language)
        self._profile_panel = ProfilePanelWidget(language=self._language)

        self._baseline_view = RasterCanvasView()
        self._candidate_view = RasterCanvasView()
        self._diff_view = RasterCanvasView()
        self._single_view = RasterCanvasView()
        self._baseline_pane = ViewPaneWidget(t(self._language, "tab.baseline"), self._baseline_view)
        self._candidate_pane = ViewPaneWidget(t(self._language, "tab.candidate"), self._candidate_view)
        self._diff_pane = ViewPaneWidget(t(self._language, "tab.diff"), self._diff_view, show_title=False)
        self._single_pane = ViewPaneWidget(t(self._language, "tab.baseline"), self._single_view, show_title=False)
        self._single_selector = QComboBox()
        self._single_selector.addItem("", "baseline")
        self._single_selector.addItem("", "candidate")

        self._channel_selector = QComboBox()
        self._populate_channel_selector()
        self._scale_selector = QComboBox()
        self._populate_scale_selector()
        self._language_selector = QComboBox()
        for code, label in language_display_items():
            self._language_selector.addItem(label, code)
        self._language_selector.setCurrentIndex(self._language_selector.findData(self._language))
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

        self._build_ui()
        self._wire_signals()
        self.retranslate_ui()
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

    @property
    def _repo_root(self) -> Path:
        return self._repo_root_path

    @_repo_root.setter
    def _repo_root(self, value: Path) -> None:
        resolved = Path(value).resolve()
        self._repo_root_path = resolved
        if hasattr(self, "_state"):
            self._state.update_repo_root(resolved)
        if hasattr(self, "_help_actions"):
            self._help_actions.update_repo_root(resolved)

    @property
    def _cases_root(self) -> Path:
        return self._state.cases_root

    @property
    def _preset_root(self) -> Path:
        return self._state.preset_root

    @_preset_root.setter
    def _preset_root(self, value: Path) -> None:
        self._state.update_preset_root(Path(value))

    @property
    def _current_case_path(self) -> Path:
        return self._state.current_case_path

    @_current_case_path.setter
    def _current_case_path(self, value: Path) -> None:
        self._state.current_case_path = Path(value)

    @property
    def _current_input_kind(self) -> str:
        return self._state.current_input_kind

    @_current_input_kind.setter
    def _current_input_kind(self, value: str) -> None:
        self._state.current_input_kind = value

    @property
    def _snapshot(self):
        return self._state.snapshot

    @_snapshot.setter
    def _snapshot(self, value) -> None:
        self._state.snapshot = value

    @property
    def _default_context(self):
        return self._state.default_context

    @_default_context.setter
    def _default_context(self, value) -> None:
        self._state.default_context = value

    @property
    def _working_context(self):
        return self._state.working_context

    @_working_context.setter
    def _working_context(self, value) -> None:
        self._state.working_context = value

    @property
    def _baseline_state(self):
        return self._state.baseline_state

    @_baseline_state.setter
    def _baseline_state(self, value) -> None:
        self._state.baseline_state = value

    @property
    def _candidate_state(self):
        return self._state.candidate_state

    @_candidate_state.setter
    def _candidate_state(self, value) -> None:
        self._state.candidate_state = value

    @property
    def _baseline_config(self) -> FieldConfig:
        return self._state.baseline_config

    @_baseline_config.setter
    def _baseline_config(self, value: FieldConfig) -> None:
        self._state.baseline_config = value

    @property
    def _candidate_config(self) -> FieldConfig:
        return self._state.candidate_config

    @_candidate_config.setter
    def _candidate_config(self, value: FieldConfig) -> None:
        self._state.candidate_config = value

    @property
    def _async(self):
        return self._coordinator.evaluator

    @property
    def _parameter_help_dialog(self):
        return self._help_actions.parameter_help_dialog

    @property
    def _lab_help_dialog(self):
        return self._help_actions.guide_dialog

    def closeEvent(self, event) -> None:
        self._coordinator.shutdown()
        super().closeEvent(event)

    def export_current_comparison(self) -> Path | None:
        if self._comparison_result is None:
            return None
        from driving_preference_field.profile_inspection import export_profile_bundle
        from driving_preference_field.rendering import render_case, render_diff_image

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
        if self._profile_result is None:
            self._refresh_profile_panel()
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
        self._case_dock = self._add_dock("", self._case_panel, Qt.DockWidgetArea.LeftDockWidgetArea)
        self._left_tabs = QTabWidget()
        self._left_tabs.addTab(self._preset_panel, "")
        self._left_tabs.addTab(self._summary_panel, "")
        self._left_tabs.addTab(self._profile_panel, "")
        self._left_tabs.addTab(self._layer_panel, "")
        self._left_tabs.setDocumentMode(True)
        self._left_tabs.currentChanged.connect(self._on_left_tab_changed)
        self._left_stack_dock = self._add_dock("", self._left_tabs, Qt.DockWidgetArea.LeftDockWidgetArea)

        self._parameter_tabs = QTabWidget()
        self._parameter_tabs.addTab(self._wrap_scroll(self._baseline_panel), "")
        self._parameter_tabs.addTab(self._wrap_scroll(self._candidate_panel), "")
        self._parameter_tabs.setDocumentMode(True)
        self._parameter_dock = self._add_dock("", self._parameter_tabs, Qt.DockWidgetArea.RightDockWidgetArea)

        self._case_dock.setMinimumWidth(0)
        self._left_stack_dock.setMinimumWidth(0)
        self._parameter_dock.setMinimumWidth(320)
        self.splitDockWidget(self._case_dock, self._left_stack_dock, Qt.Orientation.Vertical)
        self.resizeDocks([self._case_dock, self._left_stack_dock], [330, 400], Qt.Orientation.Vertical)
        self.statusBar().addPermanentWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._hover_label, 2)

    def _build_toolbar(self) -> None:
        self._toolbar = QToolBar()
        self._toolbar.setMovable(False)
        self.addToolBar(self._toolbar)

        self._reload_action = QAction(self)
        self._reload_action.setShortcut("F5")
        self._reload_action.triggered.connect(self._reload_case)

        self._export_action = QAction(self)
        self._export_action.setShortcut("Ctrl+Shift+E")
        self._export_action.triggered.connect(self._export_comparison)

        self._reset_view_action = QAction(self)
        self._reset_view_action.setShortcut("Ctrl+0")
        self._reset_view_action.triggered.connect(self._reset_views)

        self._lab_help_action = QAction(self)
        self._lab_help_action.setShortcut("F1")
        self._lab_help_action.triggered.connect(self._show_lab_help)

        self._channel_label = QLabel()
        self._scale_label = QLabel()
        self._language_label = QLabel()

        self._toolbar.addAction(self._reload_action)
        self._toolbar.addAction(self._export_action)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._reset_view_action)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(self._channel_label)
        self._toolbar.addWidget(self._channel_selector)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(self._scale_label)
        self._toolbar.addWidget(self._scale_selector)
        self._toolbar.addWidget(self._scale_info_label)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(self._language_label)
        self._toolbar.addWidget(self._language_selector)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._lab_help_action)

    def _build_central_tabs(self) -> None:
        self._tabs = QTabWidget()

        self._compare_splitter = QSplitter(COMPARE_LAYOUT_OPTIONS[self._compare_layout])
        self._compare_splitter.addWidget(self._baseline_pane)
        self._compare_splitter.addWidget(self._candidate_pane)
        self._compare_splitter.setSizes([1, 1])
        compare_container = CompareTabWidget(self._compare_splitter, self._compare_layout_button)

        single_container = QWidget()
        single_layout = QVBoxLayout(single_container)
        single_layout.addWidget(self._single_selector)
        single_layout.addWidget(self._single_pane)
        self._tabs.addTab(single_container, "")
        self._tabs.addTab(compare_container, "")
        self._tabs.addTab(self._diff_pane, "")

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
        self._language_selector.currentIndexChanged.connect(self._on_language_changed)
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

    def _populate_channel_selector(self) -> None:
        self._channel_selector.blockSignals(True)
        self._channel_selector.clear()
        for channel_name in CHANNEL_OPTIONS:
            self._channel_selector.addItem(t(self._language, f"channel.{channel_name}"), channel_name)
        self._channel_selector.setCurrentIndex(self._channel_selector.findData(self._selected_channel))
        self._channel_selector.blockSignals(False)

    def _populate_scale_selector(self) -> None:
        self._scale_selector.blockSignals(True)
        self._scale_selector.clear()
        self._scale_selector.addItem(t(self._language, "scale.fixed"), SCALE_MODE_FIXED)
        self._scale_selector.addItem(t(self._language, "scale.normalized"), SCALE_MODE_NORMALIZED)
        self._scale_selector.setCurrentIndex(self._scale_selector.findData(self._scale_mode))
        self._scale_selector.blockSignals(False)

    def retranslate_ui(self) -> None:
        self.setWindowTitle(t(self._language, "app.title"))
        self._toolbar.setWindowTitle(t(self._language, "app.title"))
        self._reload_action.setText(t(self._language, "toolbar.reload"))
        self._reload_action.setStatusTip(t(self._language, "toolbar.status.reload"))
        self._export_action.setText(t(self._language, "toolbar.export"))
        self._export_action.setStatusTip(t(self._language, "toolbar.status.export"))
        self._reset_view_action.setText(t(self._language, "toolbar.reset_view"))
        self._reset_view_action.setStatusTip(t(self._language, "toolbar.status.reset_view"))
        self._lab_help_action.setText(t(self._language, "toolbar.guide"))
        self._lab_help_action.setStatusTip(t(self._language, "toolbar.status.guide"))
        self._channel_label.setText(t(self._language, "toolbar.channel"))
        self._scale_label.setText(t(self._language, "toolbar.scale"))
        self._language_label.setText(t(self._language, "toolbar.language"))
        self._populate_channel_selector()
        self._populate_scale_selector()
        self._language_selector.blockSignals(True)
        self._language_selector.setCurrentIndex(self._language_selector.findData(self._language))
        self._language_selector.blockSignals(False)
        self._case_dock.setWindowTitle(t(self._language, "dock.case_controls"))
        self._left_stack_dock.setWindowTitle(t(self._language, "dock.workspace"))
        self._parameter_dock.setWindowTitle(t(self._language, "dock.parameters"))
        self._left_tabs.setTabText(0, t(self._language, "tab.presets"))
        self._left_tabs.setTabText(1, t(self._language, "tab.summary"))
        self._left_tabs.setTabText(2, t(self._language, "tab.profile"))
        self._left_tabs.setTabText(3, t(self._language, "tab.layers"))
        self._parameter_tabs.setTabText(0, t(self._language, "tab.baseline"))
        self._parameter_tabs.setTabText(1, t(self._language, "tab.candidate"))
        self._tabs.setTabText(0, t(self._language, "tab.single"))
        self._tabs.setTabText(1, t(self._language, "tab.compare"))
        self._tabs.setTabText(2, t(self._language, "tab.diff"))
        self._baseline_pane.set_title(t(self._language, "tab.baseline"))
        self._candidate_pane.set_title(t(self._language, "tab.candidate"))
        self._single_pane.set_title(
            t(self._language, "tab.baseline") if self._single_side == "baseline" else t(self._language, "tab.candidate")
        )
        self._status_label.setText(
            t(self._language, "status.computing") if self._busy else t(self._language, "status.idle")
        )
        self._case_panel.retranslate(self._language)
        self._layer_panel.retranslate(self._language)
        self._preset_panel.retranslate(self._language)
        self._summary_panel.retranslate(self._language)
        self._profile_panel.retranslate(self._language)
        self._baseline_panel.retranslate(self._language, title=t(self._language, "panel.baseline_progression"))
        self._candidate_panel.retranslate(self._language, title=t(self._language, "panel.candidate_progression"))
        self._single_selector.blockSignals(True)
        self._single_selector.setItemText(0, t(self._language, "single.selector.baseline"))
        self._single_selector.setItemText(1, t(self._language, "single.selector.candidate"))
        self._single_selector.blockSignals(False)
        self._update_compare_layout_button()
        self._help_actions.retranslate(self._language)

    def _on_language_changed(self) -> None:
        self._language = normalize_language(str(self._language_selector.currentData()))
        self._settings.setValue("ui/language", self._language)
        self.retranslate_ui()
        self._refresh_views()
        self._refresh_profile_panel()

    def _initialize_side_from_path(self, side: str, preset_path: Path | None) -> None:
        self._state.initialize_side_from_path(side, preset_path)

    def _normalize_case_path(self, case_path: Path | str) -> Path:
        return self._state.normalize_case_path(case_path)

    def _set_side_from_preset(
        self,
        side: str,
        preset: ComparisonPreset,
        *,
        source_path: Path | None,
        unsaved: bool,
        schedule: bool = True,
    ) -> None:
        self._state.set_side_from_preset(side, preset, source_path=source_path, unsaved=unsaved)
        if side == "baseline" and hasattr(self, "_baseline_panel"):
            self._baseline_panel.set_config(self._baseline_config)
        if side == "candidate" and hasattr(self, "_candidate_panel"):
            self._candidate_panel.set_config(self._candidate_config)
        if schedule:
            self._schedule_evaluation()

    def _mark_side_unsaved(self, side: str) -> None:
        self._state.mark_side_unsaved(side)

    def _refresh_preset_list(self) -> None:
        baseline_descriptors, candidate_descriptors = self._state.grouped_preset_descriptors()
        self._preset_panel.set_presets(
            baseline_presets=baseline_descriptors,
            candidate_presets=candidate_descriptors,
        )

    def _reload_case(self) -> None:
        self._state.reload_case()
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
        self._coordinator.request(
            self._snapshot,
            self._working_context,
            baseline_config=self._baseline_config,
            candidate_config=self._candidate_config,
            x_samples=160,
            y_samples=160,
        )

    def _on_case_changed(self, case_path: str) -> None:
        self._state.load_case(case_path)
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
        self._state.apply_case_controls(ego_pose, local_window)
        self._profile_panel.set_context(self._working_context)
        self._profile_result = None
        self._reset_views_pending = True
        self._schedule_evaluation()

    def _on_case_controls_reset(self) -> None:
        self._state.reset_case_controls()
        self._profile_panel.set_context(self._working_context)
        self._profile_result = None
        self._reset_views_pending = True
        self._schedule_evaluation()

    def _on_baseline_config_changed(self, config: FieldConfig) -> None:
        self._state.update_side_config("baseline", config)
        self._schedule_evaluation()

    def _on_candidate_config_changed(self, config: FieldConfig) -> None:
        self._state.update_side_config("candidate", config)
        self._schedule_evaluation()

    def _load_preset_into_side(self, side: str, preset_path: str) -> None:
        self._state.load_preset_into_side(side, preset_path)
        if side == "baseline":
            self._baseline_panel.set_config(self._baseline_config)
        else:
            self._candidate_panel.set_config(self._candidate_config)
        self._schedule_evaluation()

    def _save_preset_from_side(self, side: str, preset_name: str) -> None:
        saved, message = self._state.save_preset_from_side(side, preset_name)
        if not saved:
            QMessageBox.warning(
                self,
                t(self._language, "message.preset_save_rejected.title"),
                message or t(self._language, "message.preset_save_rejected.body_default"),
            )
            return
        self._refresh_preset_list()
        self._refresh_summary()

    def _copy_side(self, source: str, target: str) -> None:
        self._state.copy_side(source, target)
        if target == "baseline":
            self._baseline_panel.set_config(self._baseline_config)
        else:
            self._candidate_panel.set_config(self._candidate_config)
        self._schedule_evaluation()

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
        orientation = COMPARE_LAYOUT_OPTIONS[self._compare_layout]
        self._compare_splitter.setOrientation(orientation)
        self._compare_splitter.setSizes([1, 1])
        self._update_compare_layout_button()

    def _update_compare_layout_button(self) -> None:
        if self._compare_layout == "stacked":
            self._compare_layout_button.setText("↔")
            self._compare_layout_button.setToolTip(t(self._language, "toolbar.compare_layout.to_side_by_side"))
        else:
            self._compare_layout_button.setText("↕")
            self._compare_layout_button.setToolTip(t(self._language, "toolbar.compare_layout.to_stacked"))

    def _on_single_side_changed(self, value: str) -> None:
        self._single_side = str(self._single_selector.currentData() or value)
        self._single_pane.set_title(
            t(self._language, "tab.baseline") if self._single_side == "baseline" else t(self._language, "tab.candidate")
        )
        self._refresh_views()

    def _on_note_changed(self, value: str) -> None:
        self._qualitative_note = value

    def _on_comparison_ready(self, _generation: int, result: RasterComparisonResult) -> None:
        self._comparison_result = result
        self._refresh_views()
        self._profile_result = None
        self._profile_panel.set_profile_result(None, selected_channel=self._selected_channel)
        if self._left_tabs.currentWidget() is self._profile_panel:
            self._refresh_profile_panel()
        if self._reset_views_pending:
            self._reset_views()
            self._reset_views_pending = False
        self._refresh_summary()

    def _on_evaluation_failed(self, _generation: int, message: str) -> None:
        QMessageBox.critical(self, t(self._language, "message.evaluation_failed.title"), message)

    def _on_busy_changed(self, busy: bool) -> None:
        self._busy = busy
        self._status_label.setText(t(self._language, "status.computing") if busy else t(self._language, "status.idle"))

    def _on_profile_spec_changed(self, _axis: str, _coordinate: float) -> None:
        self._profile_result = None
        if self._left_tabs.currentWidget() is self._profile_panel:
            self._refresh_profile_panel()
        self._refresh_summary()

    def _on_left_tab_changed(self, _index: int) -> None:
        if self._left_tabs.currentWidget() is self._profile_panel and self._profile_result is None:
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
        label = t(self._language, f"channel.{self._selected_channel}")
        cmap = CHANNEL_OPTIONS[self._selected_channel]
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
        self._status_label.setText(t(self._language, "status.idle_channel", label=label))

    def _refresh_profile_panel(self) -> None:
        if self._comparison_result is None:
            self._profile_result = None
            self._profile_panel.set_profile_result(None, selected_channel=self._selected_channel)
            return
        try:
            from driving_preference_field.profile_inspection import build_comparison_profile

            self._profile_result = build_comparison_profile(
                self._comparison_result.baseline_raster,
                self._comparison_result.candidate_raster,
                spec=self._profile_panel.profile_spec(),
                selected_channel=self._selected_channel,
            )
            self._profile_panel.set_profile_result(self._profile_result, selected_channel=self._selected_channel)
        except Exception as exc:
            LOGGER.exception("Profile comparison build failed: %s", exc)
            self._profile_result = None
            self._profile_panel.set_profile_result(None, selected_channel=self._selected_channel)
            self._profile_panel.setToolTip(f"Profile comparison unavailable: {exc}")

    def _refresh_summary(self) -> None:
        if self._comparison_result is None:
            return
        summary = summary_payload(
            state=self._state,
            comparison_result=self._comparison_result,
            selected_channel=self._selected_channel,
            scale_mode=self._scale_mode,
            profile_result=self._current_profile_result(),
            qualitative_note=self._qualitative_note,
        )
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
        if self._profile_result is None and self._left_tabs.currentWidget() is self._profile_panel:
            self._refresh_profile_panel()
        return self._profile_result

    def _profile_summary_payload(self) -> dict[str, object]:
        result = self._current_profile_result()
        if result is None:
            return {
                "available": False,
                "selected_channel": self._selected_channel,
            }
        from driving_preference_field.profile_inspection import summarize_profile_result

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
            "progression_total": state_result.base_preference_total,
            "selected_channel_value": self._state_channel_value(state_result, self._selected_channel),
        }

    def _diff_summary_payload(self, baseline_state, candidate_state) -> dict[str, object]:
        baseline_selected = self._state_channel_value(baseline_state, self._selected_channel)
        candidate_selected = self._state_channel_value(candidate_state, self._selected_channel)
        return {
            "selected_channel_delta": (
                None
                if baseline_selected is None or candidate_selected is None
                else candidate_selected - baseline_selected
            ),
            "progression_total_delta": candidate_state.base_preference_total - baseline_state.base_preference_total,
            "diff_raster_summary": _summarize_diff_array(self._selected_diff_array()),
        }

    def _visualization_payload(self) -> dict[str, object]:
        baseline_data = self._comparison_result.baseline_raster.channels[self._selected_channel]
        candidate_data = self._comparison_result.candidate_raster.channels[self._selected_channel]
        diff_data = self._selected_diff_array()
        return {
            "scale_mode": self._scale_mode,
            "score_sign": "higher is better",
            "progression_surface_kind": "guide-local blended progress coordinates + exact raw-guide distance transverse term + hard max envelope",
            "raster_role": "visualization only",
            "selected_channel_unit": display_unit(self._selected_channel),
            "diff_unit": display_unit(self._selected_channel, diff=True),
            "baseline_range": self._display_range(baseline_data, diff=False),
            "candidate_range": self._display_range(candidate_data, diff=False),
            "diff_range": self._display_range(diff_data, diff=True),
        }

    def _state_channel_value(self, state_result, channel_name: str) -> float | None:
        if channel_name in state_result.base_preference_channels:
            return state_result.base_preference_channels[channel_name]
        debug_key_map = {
            "progression_s_hat": "progression_s_hat",
            "progression_center_distance": "progression_center_distance",
            "progression_longitudinal_component": "progression_longitudinal_component",
            "progression_transverse_term": "progression_transverse_term",
            "progression_support_mod": "progression_support_mod",
            "progression_alignment_mod": "progression_alignment_mod",
        }
        if channel_name in debug_key_map:
            return float(state_result.diagnostics[debug_key_map[channel_name]])
        return None

    def _export_comparison(self) -> None:
        if not self._confirm_export_comparison():
            return
        export_path = self.export_current_comparison()
        if export_path is None:
            return
        QMessageBox.information(self, t(self._language, "message.export_complete.title"), str(export_path))

    def _confirm_export_comparison(self) -> bool:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle(t(self._language, "message.export_confirm.title"))
        dialog.setText(t(self._language, "message.export_confirm.body"))
        dialog.setInformativeText(t(self._language, "message.export_confirm.detail"))

        export_button = dialog.addButton(
            t(self._language, "message.export_confirm.action"),
            QMessageBox.ButtonRole.AcceptRole,
        )
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        cancel_button = dialog.button(QMessageBox.StandardButton.Cancel)
        if cancel_button is not None:
            dialog.setDefaultButton(cancel_button)
            dialog.setEscapeButton(cancel_button)

        dialog.exec()
        return dialog.clickedButton() is export_button

    def _show_parameter_help(self) -> None:
        self._help_actions.show_parameter_help(self._language)

    def _show_lab_help(self) -> None:
        self._help_actions.show_guide(self._language)

    def _current_baseline_preset(self):
        return self._state.current_baseline_preset()

    def _current_candidate_preset(self):
        return self._state.current_candidate_preset()

    def _build_comparison_session(
        self,
        *,
        baseline_render_summary: dict[str, object],
        candidate_render_summary: dict[str, object],
        profile_summary: dict[str, object],
        exported_at: str,
    ):
        assert self._comparison_result is not None
        return build_comparison_session(
            state=self._state,
            comparison_result=self._comparison_result,
            selected_channel=self._selected_channel,
            scale_mode=self._scale_mode,
            qualitative_note=self._qualitative_note,
            baseline_render_summary=baseline_render_summary,
            candidate_render_summary=candidate_render_summary,
            profile_summary=profile_summary,
            exported_at=exported_at,
        )
