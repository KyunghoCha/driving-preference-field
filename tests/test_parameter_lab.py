from pathlib import Path
import ast
import json

import pytest
from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, QSettings, Qt, QUrl
from PyQt6.QtGui import QColor, QImage

from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, LANG_EN, LANG_KO, UI_TEXTS, guide_doc_path
from driving_preference_field.ui.parameter_guide import PANEL_NOTE_TEXT, parameter_help_html
from driving_preference_field.ui.parameter_lab_window import ParameterLabWindow


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/adapter"
PRODUCT_LABELS = {"Guide", "Parameter Help", "Main", "Advanced Surface", "Profile", "Baseline", "Candidate", "Diff", "channel", "scale"}


@pytest.fixture(autouse=True)
def _clear_parameter_lab_settings() -> None:
    settings = QSettings("driving-preference-field", "ParameterLab")
    settings.clear()
    settings.sync()
    yield
    settings.clear()
    settings.sync()


def _wait_for_result(qtbot, window: ParameterLabWindow) -> None:
    qtbot.waitUntil(lambda: window._comparison_result is not None, timeout=15000)


def _png_bytes(width: int, height: int) -> bytes:
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor("#336699"))
    payload = QByteArray()
    buffer = QBuffer(payload)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "PNG")
    return bytes(payload)


def test_parameter_lab_window_opens_and_populates_compare_views(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()

    _wait_for_result(qtbot, window)

    assert window._comparison_result is not None
    assert window._profile_result is None
    assert window._baseline_view.scene() is not None
    assert window._candidate_view.scene() is not None
    assert window._left_tabs.count() == 4
    assert window._left_tabs.tabText(2) == "Profile"
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
    assert window._reload_action.text() == "Reload Case"
    assert window._export_action.text() == "Export Comparison"
    assert window._reset_view_action.text() == "Reset View"
    assert window._lab_help_action.text() == "Guide"
    assert window._reload_action.shortcut().toString() == "F5"
    assert window._export_action.shortcut().toString() == "Ctrl+Shift+E"
    assert window._reset_view_action.shortcut().toString() == "Ctrl+0"
    assert window._lab_help_action.shortcut().toString() == "F1"
    assert window._reset_view_action.shortcut().toString() == "Ctrl+0"
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
    assert "anchor_spacing_m" in window._baseline_panel._controls
    assert "transverse_handoff_temperature" in window._baseline_panel._controls
    assert window._baseline_panel._advanced_toggle.isChecked() is False
    assert window._baseline_panel._advanced_content.isVisible() is False
    assert window._channel_selector.findData("progression_s_hat") != -1
    assert window._channel_selector.findData("progression_transverse_component") != -1
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
    assert window._case_dock.minimumWidth() < 300
    assert window._left_stack_dock.minimumWidth() < 300
    summary = json.loads(window._summary_panel._text.toPlainText())
    assert summary["profile"]["available"] is False
    assert summary["profile"]["selected_channel"] == "progression_tilted"

    window.close()


def test_locale_catalog_stays_complete_and_mixed_terms_remain_consistent() -> None:
    assert set(UI_TEXTS[LANG_EN]) == set(UI_TEXTS[LANG_KO])
    for language in (LANG_EN, LANG_KO):
        for key, value in UI_TEXTS[language].items():
            assert value.strip(), key

    assert UI_TEXTS[LANG_KO]["toolbar.guide"] == "Guide"
    assert UI_TEXTS[LANG_KO]["toolbar.parameter_help"] == "Parameter Help"
    assert UI_TEXTS[LANG_KO]["dock.parameters"] == "Parameters"
    assert UI_TEXTS[LANG_KO]["tab.profile"] == "Profile"
    assert UI_TEXTS[LANG_KO]["tab.baseline"] == "Baseline"
    assert UI_TEXTS[LANG_KO]["tab.candidate"] == "Candidate"
    assert UI_TEXTS[LANG_KO]["param.section.advanced"] == "Advanced Surface"
    assert UI_TEXTS[LANG_KO]["param.button.apply"] == "Apply"
    assert UI_TEXTS[LANG_KO]["toolbar.channel"] == "channel"
    assert UI_TEXTS[LANG_KO]["toolbar.scale"] == "scale"
    assert UI_TEXTS[LANG_KO]["help.guide.title"] == "Guide"
    assert UI_TEXTS[LANG_KO]["help.parameter.title"] == "Parameter Help"


def test_guide_and_parameter_help_keep_distinct_roles_in_both_languages() -> None:
    help_en = parameter_help_html(LANG_EN)
    help_ko = parameter_help_html(LANG_KO)
    guide_en = guide_doc_path(ROOT, LANG_EN).read_text(encoding="utf-8")
    guide_ko = guide_doc_path(ROOT, LANG_KO).read_text(encoding="utf-8")

    assert "This page explains the controls" in help_en
    assert "이 도움말은 오른쪽" in help_ko
    assert "Quick start" in guide_en
    assert "빠른 시작" in guide_ko
    assert "what each control changes" in help_en
    assert "각 항목이 무엇을 바꾸는지" in help_ko


def test_high_risk_ui_modules_do_not_hardcode_product_labels() -> None:
    ui_root = ROOT / "src" / "driving_preference_field" / "ui"
    targets = [ui_root / "parameter_lab_window.py", *sorted((ui_root / "widgets").glob("*.py"))]
    offenders: list[str] = []

    for path in targets:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        for literal in sorted(PRODUCT_LABELS & literals):
            offenders.append(f"{path.relative_to(ROOT)} -> {literal}")

    assert not offenders, "\n".join(offenders)


def test_profile_panel_builds_on_demand_when_profile_tab_is_selected(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()

    _wait_for_result(qtbot, window)

    assert window._profile_result is None
    window._left_tabs.setCurrentIndex(2)

    qtbot.waitUntil(lambda: window._profile_result is not None, timeout=15000)
    summary = json.loads(window._summary_panel._text.toPlainText())
    assert summary["profile"]["available"] is True

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


def test_parameter_lab_accepts_generic_adapter_input_path(qtbot) -> None:
    case_path = FIXTURES / "straight_corridor_generic.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()

    _wait_for_result(qtbot, window)

    assert window._current_case_path.name == "straight_corridor_generic.yaml"
    assert window._current_input_kind == "generic_adapter"
    assert window._case_panel.current_case_path() is not None
    assert Path(window._case_panel.current_case_path()).name == "straight_corridor_generic.yaml"

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
    assert '"selected_channel_unit": "cost score"' in summary_text

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
    window._baseline_panel._advanced_toggle.click()
    window._baseline_panel._controls["anchor_spacing_m"].setValue(0.3)
    assert abs(window._baseline_config.progression.longitudinal_gain - 1.75) > 1e-6
    assert abs(window._baseline_config.surface_tuning.anchor_spacing_m - 0.3) > 1e-6
    window._baseline_panel._apply_button.click()
    qtbot.waitUntil(
        lambda: abs(window._baseline_config.progression.longitudinal_gain - 1.75) < 1e-6,
        timeout=15000,
    )
    qtbot.waitUntil(
        lambda: abs(window._baseline_config.surface_tuning.anchor_spacing_m - 0.3) < 1e-6,
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
    assert (export_path / "baseline" / "progression_tilted.png").exists()
    assert (export_path / "candidate" / "progression_tilted.png").exists()
    session_path = export_path / "comparison_session.json"
    assert session_path.exists()
    assert (export_path / "profile" / "profile_baseline.png").exists()
    assert (export_path / "profile" / "profile_candidate.png").exists()
    assert (export_path / "profile" / "profile_diff.png").exists()
    assert (export_path / "profile" / "profile_data.json").exists()
    assert any(path.name.startswith("diff_") for path in export_path.iterdir())
    session = json.loads(session_path.read_text(encoding="utf-8"))
    assert session["note"] == "candidate prefers stronger longitudinal field"
    assert session["baseline_preset"]["preset_name"]
    assert session["candidate_preset"]["preset_name"]
    assert session["baseline_preset"]["metadata"]["unsaved"] is True
    assert session["candidate_preset"]["metadata"]["unsaved"] is True
    assert session["selected_channel"] == window._selected_channel
    assert "raster" in session["diff_summary"]
    assert (
        session["diff_summary"]["visualization"]["progression_surface_kind"]
        == "guide-local blended coordinates with hard max envelope"
    )
    assert session["diff_summary"]["visualization"]["raster_role"] == "visualization only"
    assert session["diff_summary"]["visualization"]["score_sign"] == "higher is better"
    assert session["profile_summary"]["selected_channel"] == window._selected_channel
    assert session["profile_summary"]["available"] is True
    assert session["profile_summary"]["file_manifest"]["profile_data.json"].endswith("profile_data.json")
    assert session["effective_ego_pose"]["x"] == window._working_context.ego_pose.x
    assert session["effective_local_window"]["y_min"] == window._working_context.local_window.y_min
    baseline_progression = session["baseline_preset"]["field_config"]["progression"]
    candidate_progression = session["candidate_preset"]["field_config"]["progression"]
    baseline_surface = session["baseline_preset"]["field_config"]["surface_tuning"]
    candidate_surface = session["candidate_preset"]["field_config"]["surface_tuning"]
    assert "model" not in baseline_progression
    assert "transverse" + "_penalty_weight" not in candidate_progression
    assert baseline_progression["longitudinal_frame"] in {"local_absolute", "ego_relative"}
    assert candidate_progression["longitudinal_frame"] in {"local_absolute", "ego_relative"}
    assert "longitudinal_family" in baseline_progression
    assert "transverse_family" in candidate_progression
    assert baseline_surface["anchor_spacing_m"] == 0.3
    assert candidate_surface["anchor_spacing_m"] == 0.3

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
    assert "Parameter Help" in help_text
    assert "Start Here" in help_text
    assert "Main vs Advanced" in help_text
    assert "Detailed Reference" in help_text
    assert "practical band" in help_text.lower()
    assert "technical range" in help_text.lower()
    assert "0.5 .. 3.0" in help_text
    assert "Advanced Surface" in help_text
    assert "anchor spacing" in help_text
    assert "candidate - baseline" in help_text
    assert "progression_tilted" in help_text
    assert "`progression_tilted`" not in help_text
    assert "Guide" in help_text
    assert "continuous field" in help_text.lower()
    assert "raster" in help_text.lower()
    assert "longitudinal" in help_text.lower()
    assert "transverse" in help_text.lower()
    assert ("prototype" + "_ridge") not in help_text
    assert ("surface" + "_v2") not in help_text
    assert window._baseline_panel._note_label.text() == PANEL_NOTE_TEXT[DEFAULT_LANGUAGE]
    assert "Recommended 0.5..3.0" in window._baseline_panel._controls["longitudinal_gain"].toolTip()
    assert "Technical range:" in window._baseline_panel._controls["transverse_family"].toolTip()

    window.close()


def test_toolbar_docs_opens_parameter_lab_docs_browser(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    window._lab_help_action.trigger()

    qtbot.waitUntil(
        lambda: window._lab_help_dialog is not None and window._lab_help_dialog.isVisible(),
        timeout=15000,
    )
    assert window._lab_help_dialog is not None
    assert window._lab_help_dialog.windowTitle() == "Guide"
    help_text = window._lab_help_dialog._text.toPlainText()
    assert "Parameter Lab Guide" in help_text
    assert "Quick start" in help_text
    assert "How to read the screen" in help_text
    assert "Guide vs Parameter Help" in help_text

    window._lab_help_dialog._text.setSource(QUrl("../explanation/parameter_exposure_policy.md"))
    qtbot.waitUntil(
        lambda: "Parameter Exposure Policy" in window._lab_help_dialog._text.toPlainText(),
        timeout=15000,
    )
    assert window._lab_help_dialog._text.isBackwardAvailable() is True
    window._lab_help_dialog._text.backward()
    qtbot.waitUntil(
        lambda: "Parameter Lab Guide" in window._lab_help_dialog._text.toPlainText(),
        timeout=15000,
    )

    window.close()


def test_language_switch_retranslates_ui_and_persists(qtbot) -> None:
    settings = QSettings("driving-preference-field", "ParameterLab")
    settings.clear()
    settings.sync()

    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    assert window._language == DEFAULT_LANGUAGE
    assert window._left_tabs.tabText(2) == "Profile"
    assert window._lab_help_action.text() == "Guide"

    index = window._language_selector.findData(LANG_KO)
    window._language_selector.setCurrentIndex(index)

    qtbot.waitUntil(lambda: window._language == LANG_KO, timeout=15000)
    assert window._left_tabs.tabText(2) == "Profile"
    assert window._parameter_dock.windowTitle() == "Parameters"
    assert window._lab_help_action.text() == "Guide"
    assert window._baseline_panel._apply_button.text() == "Apply"

    window._baseline_panel._help_button.click()
    qtbot.waitUntil(
        lambda: window._parameter_help_dialog is not None and window._parameter_help_dialog.isVisible(),
        timeout=15000,
    )
    assert "Parameter Help" in window._parameter_help_dialog.windowTitle()

    window._lab_help_action.trigger()
    qtbot.waitUntil(
        lambda: window._lab_help_dialog is not None and window._lab_help_dialog.isVisible(),
        timeout=15000,
    )
    assert "빠른 시작" in window._lab_help_dialog._text.toPlainText()

    window.close()

    reopened = ParameterLabWindow(case_path=case_path)
    reopened.show()
    _wait_for_result(qtbot, reopened)
    assert reopened._language == LANG_KO
    assert reopened._left_tabs.tabText(2) == "Profile"
    reopened.close()


def test_advanced_surface_controls_apply_reset_and_reload(qtbot, tmp_path) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    panel = window._baseline_panel
    panel._advanced_toggle.click()
    assert panel._advanced_toggle.isChecked() is True
    assert panel._advanced_content.isVisible() is True

    original = window._baseline_config.surface_tuning.anchor_spacing_m
    panel._controls["anchor_spacing_m"].setValue(0.3)
    panel._controls["spline_min_subdivisions"].setValue(12)
    assert panel._apply_button.isEnabled() is True
    panel._reset_button.click()
    assert panel._controls["anchor_spacing_m"].value() == original
    assert panel._apply_button.isEnabled() is False

    panel._controls["anchor_spacing_m"].setValue(0.3)
    panel._controls["transverse_handoff_temperature"].setValue(0.08)
    panel._apply_button.click()
    qtbot.waitUntil(
        lambda: abs(window._baseline_config.surface_tuning.anchor_spacing_m - 0.3) < 1e-6,
        timeout=15000,
    )
    assert abs(window._baseline_config.surface_tuning.transverse_handoff_temperature - 0.08) < 1e-6

    window._preset_root = tmp_path / "presets"
    window._preset_root.mkdir(parents=True, exist_ok=True)
    window._save_preset_from_side("baseline", "advanced_surface")
    window._load_preset_into_side("candidate", str(window._preset_root / "advanced_surface.yaml"))

    assert abs(window._candidate_config.surface_tuning.anchor_spacing_m - 0.3) < 1e-6
    assert abs(window._candidate_config.surface_tuning.transverse_handoff_temperature - 0.08) < 1e-6

    window.close()


def test_profile_panel_scrollbars_activate_for_large_preview_and_reset_on_placeholder(qtbot) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    window._left_tabs.setCurrentIndex(2)
    payload = _png_bytes(2200, 1600)
    tab_specs = (
        ("Baseline", window._profile_panel._baseline_widget),
        ("Candidate", window._profile_panel._candidate_widget),
        ("Diff", window._profile_panel._diff_widget),
    )
    for _, widget in tab_specs:
        widget.set_png(payload)

    for tab_name, widget in tab_specs:
        window._profile_panel._tabs.setCurrentIndex(window._profile_panel._tabs.indexOf(widget))
        qtbot.waitUntil(
            lambda: widget._scroll.horizontalScrollBar().maximum() > 0
            and widget._scroll.verticalScrollBar().maximum() > 0,
            timeout=15000,
        )
        assert window._profile_panel._tabs.tabText(window._profile_panel._tabs.currentIndex()) == tab_name

    for _, widget in tab_specs:
        widget.set_png(None)

    for _, widget in tab_specs:
        window._profile_panel._tabs.setCurrentIndex(window._profile_panel._tabs.indexOf(widget))
        qtbot.waitUntil(
            lambda: widget._scroll.horizontalScrollBar().maximum() == 0
            and widget._scroll.verticalScrollBar().maximum() == 0,
            timeout=15000,
        )
    assert window._left_stack_dock.minimumWidth() < 300

    window.close()


def test_profile_panel_degrades_gracefully_when_plot_rendering_fails(qtbot, monkeypatch) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    window = ParameterLabWindow(case_path=case_path)
    window.show()
    _wait_for_result(qtbot, window)

    import driving_preference_field.profile_inspection as profile_inspection

    def _raise(*_args, **_kwargs):
        raise RuntimeError("synthetic render failure")

    monkeypatch.setattr(profile_inspection, "profile_plot_png_bytes", _raise)
    window._left_tabs.setCurrentIndex(2)

    qtbot.waitUntil(
        lambda: "synthetic render failure" in window._profile_panel.toolTip(),
        timeout=15000,
    )
    assert "synthetic render failure" in window._profile_panel.toolTip()

    window.close()
