from pathlib import Path

from driving_preference_field.evaluator import evaluate_state
from driving_preference_field.raster import sample_local_raster
from driving_preference_field.ui.async_raster_evaluator import RasterComparisonResult
from driving_preference_field.ui.parameter_lab.presenter import build_comparison_session, summary_payload
from driving_preference_field.ui.parameter_lab.state import ParameterLabState


ROOT = Path(__file__).resolve().parents[1]


def _comparison_result_for_state(state: ParameterLabState) -> RasterComparisonResult:
    baseline_raster = sample_local_raster(
        state.snapshot,
        state.working_context,
        config=state.baseline_config,
        x_samples=40,
        y_samples=40,
    )
    candidate_raster = sample_local_raster(
        state.snapshot,
        state.working_context,
        config=state.candidate_config,
        x_samples=40,
        y_samples=40,
    )
    baseline_state = evaluate_state(
        state.snapshot,
        state.working_context,
        state.working_context.ego_pose,
        config=state.baseline_config,
    )
    candidate_state = evaluate_state(
        state.snapshot,
        state.working_context,
        state.working_context.ego_pose,
        config=state.candidate_config,
    )
    return RasterComparisonResult(
        baseline_raster=baseline_raster,
        candidate_raster=candidate_raster,
        baseline_state=baseline_state,
        candidate_state=candidate_state,
    )


def test_summary_payload_matches_existing_public_summary_shape() -> None:
    state = ParameterLabState(repo_root=ROOT, case_path=ROOT / "cases/toy/straight_corridor.yaml")
    comparison_result = _comparison_result_for_state(state)

    summary = summary_payload(
        state=state,
        comparison_result=comparison_result,
        selected_channel="progression_tilted",
        scale_mode="fixed",
        profile_result=None,
        qualitative_note="baseline reference",
    )

    assert summary["case"].endswith("straight_corridor.yaml")
    assert summary["selected_channel"] == "progression_tilted"
    assert summary["baseline_preset_name"] == "baseline__balanced_field"
    assert summary["candidate_preset_name"] == "candidate__strong_longitudinal"
    assert summary["difference"]["diff_raster_summary"]["max"] >= summary["difference"]["diff_raster_summary"]["min"]
    assert summary["profile"]["available"] is False
    assert summary["input_kind"] == "toy_case"
    assert summary["snapshot_metadata"]["name"] == "straight_corridor"
    assert summary["progression_normalization"] is None
    assert summary["visualization"]["raster_role"] == "visualization only"


def test_summary_payload_surfaces_progression_normalization_metadata() -> None:
    state = ParameterLabState(
        repo_root=ROOT,
        case_path=ROOT / "cases/toy/u_turn_many_small_progression_guides.yaml",
    )
    comparison_result = _comparison_result_for_state(state)

    summary = summary_payload(
        state=state,
        comparison_result=comparison_result,
        selected_channel="progression_tilted",
        scale_mode="fixed",
        profile_result=None,
        qualitative_note="normalization probe",
    )

    normalization = summary["progression_normalization"]

    assert summary["input_kind"] == "toy_case"
    assert summary["snapshot_metadata"]["name"] == "u_turn_many_small_progression_guides"
    assert normalization["source_kind"] == "toy_case"
    assert normalization["applied"] is True
    assert normalization["severity"] == "warning"
    assert summary["progression_target"]["kind"] == "guide_endpoint"
    assert summary["progression_target"]["guide_id"].endswith("__normalized_chain")


def test_build_comparison_session_uses_state_and_presenter_outputs() -> None:
    state = ParameterLabState(repo_root=ROOT, case_path=ROOT / "cases/toy/straight_corridor.yaml")
    comparison_result = _comparison_result_for_state(state)

    session = build_comparison_session(
        state=state,
        comparison_result=comparison_result,
        selected_channel="progression_tilted",
        scale_mode="fixed",
        qualitative_note="session note",
        baseline_render_summary={"baseline": True},
        candidate_render_summary={"candidate": True},
        profile_summary={"available": False, "selected_channel": "progression_tilted"},
        exported_at="20260416_120000",
    )

    assert session.case_path.endswith("straight_corridor.yaml")
    assert session.selected_channel == "progression_tilted"
    assert session.note == "session note"
    assert session.baseline_preset.preset_name == "baseline__balanced_field"
    assert session.candidate_preset.preset_name == "candidate__strong_longitudinal"
    assert session.diff_summary["visualization"]["score_sign"] == "higher is better"
