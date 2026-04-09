from pathlib import Path
import json

from PyQt6.QtCore import Qt

from driving_preference_field.ui.parameter_guide import PANEL_NOTE_TEXT
from driving_preference_field.ui.parameter_lab_window import PARAMETER_HELP_TEXT, ParameterLabWindow


ROOT = Path(__file__).resolve().parents[1]


def _wait_for_result(qtbot, window: ParameterLabWindow) -> None:
    qtbot.waitUntil(lambda: window._comparison_result is not None, timeout=15000)


def test_parameter_lab_window_opens_and_populates_compare_views(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()

    _wait_for_result(qtbot, window)

    assert window._comparison_result is not None
    assert window._baseline_view.scene() is not None
    assert window._candidate_view.scene() is not None
    assert window._left_tabs.count() == 3
    assert window._parameter_tabs.count() == 2
    assert window._parameter_tabs.tabText(0) == "Baseline"
    assert window._parameter_tabs.tabText(1) == "Candidate"
    assert window._tabs.tabText(0) == "Single"
    assert window._tabs.tabText(1) == "Compare"
    assert window._tabs.tabText(2) == "Diff"
    assert window._scale_mode == "fixed"
    assert window._scale_selector.currentData() == "fixed"
    assert window._selected_channel == "progression_tilted"
    assert window._channel_selector.currentData() == "progression_tilted"
    assert window._baseline_state.preset_name == "baseline__balanced_field"
    assert window._candidate_state.preset_name == "candidate__strong_longitudinal"
    assert window._baseline_state.unsaved is False
    assert window._candidate_state.unsaved is False
    assert window._baseline_config.progression.longitudinal_frame == "local_absolute"
    assert window._candidate_config.progression.longitudinal_frame == "local_absolute"
    assert window._baseline_config.progression.longitudinal_family == "tanh"
    assert window._candidate_config.progression.longitudinal_family == "linear"
    assert "model" not in window._baseline_panel._controls
    assert "longitudinal_frame" in window._baseline_panel._controls
    assert "longitudinal_family" in window._baseline_panel._controls
    assert "transverse_family" in window._baseline_panel._controls
    assert "transverse_scale" in window._baseline_panel._controls
    window._tabs.setCurrentIndex(1)
    assert window._compare_splitter.orientation() == Qt.Orientation.Vertical
    assert window._compare_layout_button.isVisible() is True
    assert window._compare_layout_button.text() == "↔"
    assert "unit=score" in window._scale_info_label.text()
    assert window._reset_views_pending is False
    assert abs(window._baseline_view.transform().m11() - 1.0) > 1e-6
    scene_rect = window._baseline_view.sceneRect()
    local_window = window._working_context.local_window
    assert scene_rect.width() > (local_window.x_max - local_window.x_min)
    assert scene_rect.height() > (local_window.y_max - local_window.y_min)
    assert window._baseline_view.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert window._baseline_view.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert window._single_pane._title_label.isHidden() is True

    window.close()


def test_parameter_lab_relative_case_path_matches_case_panel_selection(qtbot) -> None:
    relative_case = Path("cases/toy/straight_corridor.yaml")
    window = ParameterLabWindow(case_path=relative_case)
    window.show()

    _wait_for_result(qtbot, window)

    assert window._current_case_path.name == "straight_corridor.yaml"
    assert window._case_panel.current_case_path() is not None
    assert Path(window._case_panel.current_case_path()).name == "straight_corridor.yaml"

    window.close()


def test_preset_panel_filters_reference_presets_by_role(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    baseline_paths = {
        Path(window._preset_panel._lists["baseline"].item(index).data(Qt.ItemDataRole.UserRole)).stem
        for index in range(window._preset_panel._lists["baseline"].count())
    }
    candidate_paths = {
        Path(window._preset_panel._lists["candidate"].item(index).data(Qt.ItemDataRole.UserRole)).stem
        for index in range(window._preset_panel._lists["candidate"].count())
    }

    assert "baseline__balanced_field" in baseline_paths
    assert "candidate__strong_longitudinal" in candidate_paths
    assert "candidate__strong_longitudinal" not in baseline_paths
    assert "baseline__balanced_field" not in candidate_paths

    window.close()


def test_compare_layout_button_switches_orientation(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()

    _wait_for_result(qtbot, window)

    window._tabs.setCurrentIndex(1)
    assert window._compare_splitter.orientation().name == "Vertical"
    window._compare_layout_button.click()

    assert window._compare_layout == "side_by_side"
    assert window._compare_splitter.orientation().name == "Horizontal"
    assert window._compare_layout_button.text() == "↕"

    window.close()


def test_parameter_change_recomputes_and_updates_summary(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    old_generation = window._async._latest_generation
    old_summary = window._summary_panel._text.toPlainText()
    spin = window._baseline_panel._controls["longitudinal_gain"]
    old_value = window._baseline_config.progression.longitudinal_gain
    spin.setValue(spin.value() + 0.5)

    assert window._baseline_config.progression.longitudinal_gain == old_value
    assert window._baseline_panel._apply_button.isEnabled() is True

    window._baseline_panel._apply_button.click()

    qtbot.waitUntil(lambda: window._async._latest_generation > old_generation, timeout=15000)
    qtbot.waitUntil(lambda: window._summary_panel._text.toPlainText() != old_summary, timeout=15000)
    assert window._baseline_state.unsaved is True
    assert window._baseline_state.metadata["origin"] == "user"

    window.close()


def test_selected_channel_change_updates_diff_summary(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    old_summary = window._summary_panel._text.toPlainText()
    index = window._channel_selector.findData("safety_soft")
    window._channel_selector.setCurrentIndex(index)

    qtbot.waitUntil(lambda: window._summary_panel._text.toPlainText() != old_summary, timeout=15000)
    summary_text = window._summary_panel._text.toPlainText()
    assert '"selected_channel": "safety_soft"' in summary_text
    assert '"diff_meaning": "candidate - baseline"' in summary_text
    assert '"diff_raster_summary"' in summary_text
    assert '"selected_channel_unit": "burden score"' in summary_text

    window.close()


def test_scale_mode_toggle_updates_scale_info_and_summary(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    fixed_info = window._scale_info_label.text()
    assert fixed_info.startswith("fixed")

    index = window._scale_selector.findData("normalized")
    window._scale_selector.setCurrentIndex(index)

    qtbot.waitUntil(lambda: window._scale_info_label.text() != fixed_info, timeout=15000)
    assert window._scale_mode == "normalized"
    assert window._scale_info_label.text().startswith("normalized")
    assert '"scale_mode": "normalized"' in window._summary_panel._text.toPlainText()

    window.close()


def test_case_change_recomputes_both_sides(qtbot) -> None:
    case_a = ROOT / "cases/toy/straight_corridor.yaml"
    case_b = ROOT / "cases/toy/sensor_patch_open.yaml"
    window = ParameterLabWindow(case_path=case_a)
    window.show()
    _wait_for_result(qtbot, window)

    old_generation = window._async._latest_generation
    window._case_panel.set_case_path(case_b)

    qtbot.waitUntil(lambda: window._current_case_path == case_b, timeout=15000)
    qtbot.waitUntil(lambda: window._async._latest_generation > old_generation, timeout=15000)
    _wait_for_result(qtbot, window)

    assert window._current_case_path == case_b
    assert window._working_context == window._default_context
    assert window._case_panel._controls["ego_x"].value() == window._default_context.ego_pose.x

    window.close()


def test_case_controls_apply_updates_working_context_only_after_apply(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    original_context = window._working_context
    original_generation = window._async._latest_generation

    window._case_panel._controls["ego_x"].setValue(original_context.ego_pose.x + 1.0)
    window._case_panel._controls["window_x_max"].setValue(original_context.local_window.x_max + 2.0)

    assert window._working_context == original_context
    assert window._case_panel._apply_button.isEnabled() is True
    assert window._async._latest_generation == original_generation

    window._case_panel._apply_button.click()
    qtbot.waitUntil(lambda: window._async._latest_generation > original_generation, timeout=15000)
    qtbot.waitUntil(
        lambda: abs(window._working_context.ego_pose.x - (original_context.ego_pose.x + 1.0)) < 1e-6,
        timeout=15000,
    )

    assert abs(window._working_context.local_window.x_max - (original_context.local_window.x_max + 2.0)) < 1e-6
    assert window._default_context == original_context

    window.close()


def test_case_controls_reset_restores_default_context(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    default_context = window._default_context
    window._case_panel._controls["ego_y"].setValue(default_context.ego_pose.y + 1.5)
    window._case_panel._apply_button.click()
    qtbot.waitUntil(
        lambda: abs(window._working_context.ego_pose.y - (default_context.ego_pose.y + 1.5)) < 1e-6,
        timeout=15000,
    )

    generation_after_apply = window._async._latest_generation
    window._case_panel._reset_button.click()
    qtbot.waitUntil(lambda: window._async._latest_generation > generation_after_apply, timeout=15000)
    qtbot.waitUntil(lambda: window._working_context == default_context, timeout=15000)

    assert abs(window._case_panel._controls["ego_y"].value() - default_context.ego_pose.y) < 1e-6
    assert window._case_panel._apply_button.isEnabled() is False

    window.close()


def test_layer_toggle_only_updates_overlay_visibility(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    result_before = window._comparison_result
    checkbox = window._layer_panel._checkboxes["hard_masks"]
    checkbox.setChecked(False)

    assert window._comparison_result is result_before
    assert window._baseline_view._overlay_visibility["hard_masks"] is False
    assert window._candidate_view._overlay_visibility["hard_masks"] is False

    window.close()


def test_preset_copy_and_export_workflow(qtbot, tmp_path, monkeypatch) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    window._preset_root = tmp_path / "presets"
    window._preset_root.mkdir(parents=True, exist_ok=True)
    window._save_preset_from_side("baseline", "baseline_test")
    window._refresh_preset_list()

    preset_item_text = str(window._preset_root / "baseline_test.yaml")
    window._load_preset_into_side("candidate", preset_item_text)
    assert window._candidate_config == window._baseline_config

    window._baseline_panel._controls["longitudinal_gain"].setValue(1.75)
    assert abs(window._baseline_config.progression.longitudinal_gain - 1.75) > 1e-6
    window._baseline_panel._apply_button.click()
    qtbot.waitUntil(
        lambda: abs(window._baseline_config.progression.longitudinal_gain - 1.75) < 1e-6,
        timeout=15000,
    )
    window._copy_side("baseline", "candidate")
    assert window._candidate_config == window._baseline_config
    window._case_panel._controls["ego_x"].setValue(window._default_context.ego_pose.x + 0.75)
    window._case_panel._controls["window_y_min"].setValue(window._default_context.local_window.y_min - 0.5)
    window._case_panel._apply_button.click()
    qtbot.waitUntil(
        lambda: abs(window._working_context.ego_pose.x - (window._default_context.ego_pose.x + 0.75)) < 1e-6,
        timeout=15000,
    )

    monkeypatch.setattr(window, "_repo_root", tmp_path)
    window._summary_panel.set_note("candidate prefers stronger longitudinal field")
    export_path = window.export_current_comparison()

    assert export_path is not None
    assert (export_path / "baseline" / "base_total.png").exists()
    assert (export_path / "candidate" / "base_total.png").exists()
    session_path = export_path / "comparison_session.json"
    assert session_path.exists()
    assert any(path.name.startswith("diff_") for path in export_path.iterdir())
    session = json.loads(session_path.read_text(encoding="utf-8"))
    assert session["note"] == "candidate prefers stronger longitudinal field"
    assert session["baseline_preset"]["preset_name"]
    assert session["candidate_preset"]["preset_name"]
    assert session["baseline_preset"]["metadata"]["unsaved"] is True
    assert session["candidate_preset"]["metadata"]["unsaved"] is True
    assert session["selected_channel"] == window._selected_channel
    assert "raster" in session["diff_summary"]
    assert session["effective_ego_pose"]["x"] == window._working_context.ego_pose.x
    assert session["effective_local_window"]["y_min"] == window._working_context.local_window.y_min
    baseline_progression = session["baseline_preset"]["field_config"]["progression"]
    candidate_progression = session["candidate_preset"]["field_config"]["progression"]
    assert "model" not in baseline_progression
    assert "transverse" + "_penalty_weight" not in candidate_progression
    assert baseline_progression["longitudinal_frame"] in {"local_absolute", "ego_relative"}
    assert candidate_progression["longitudinal_frame"] in {"local_absolute", "ego_relative"}
    assert "longitudinal_family" in baseline_progression
    assert "transverse_family" in candidate_progression

    window.close()


def test_saving_reference_preset_name_is_rejected(qtbot, monkeypatch) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    captured: dict[str, str] = {}

    def _fake_warning(_parent, title: str, message: str):
        captured["title"] = title
        captured["message"] = message
        return 0

    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", _fake_warning)

    window._save_preset_from_side("baseline", "baseline__balanced_field")

    assert captured["title"] == "Preset Save Rejected"
    assert "reference preset" in captured["message"]
    assert window._baseline_state.preset_name == "baseline__balanced_field"

    window.close()


def test_parameter_panel_help_opens_scrollable_dialog(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    window._baseline_panel._help_button.click()

    qtbot.waitUntil(
        lambda: window._parameter_help_dialog is not None and window._parameter_help_dialog.isVisible(),
        timeout=15000,
    )
    assert window._parameter_help_dialog is not None
    assert window._parameter_help_dialog.windowTitle() == "Parameter Help"
    assert window._parameter_help_dialog.width() >= 800
    assert window._parameter_help_dialog.height() >= 680
    help_text = window._parameter_help_dialog._text.toPlainText()
    assert "Parameter Guide" in help_text
    assert "Current Truth" in help_text
    assert "Quick Reference" in help_text
    assert "Per-Parameter Details" in help_text
    assert "practical band" in help_text.lower()
    assert "technical range" in help_text.lower()
    assert "0.5 .. 3.0" in help_text
    assert "candidate - baseline" in help_text
    assert "progression_tilted" in help_text
    assert "local_absolute" in help_text
    assert "ego_relative" in help_text
    assert "continuous function" in help_text.lower()
    assert "whole-fabric" in help_text.lower()
    assert "raster" in help_text.lower()
    assert "longitudinal" in help_text.lower()
    assert "transverse" in help_text.lower()
    assert ("prototype" + "_ridge") not in help_text
    assert ("surface" + "_v2") not in help_text
    assert PARAMETER_HELP_TEXT.strip()
    assert window._baseline_panel._note_label.text() == PANEL_NOTE_TEXT
    assert "추천 0.5..3.0" in window._baseline_panel._controls["longitudinal_gain"].toolTip()
    assert "Range:" in window._baseline_panel._controls["transverse_family"].toolTip()

    window.close()
