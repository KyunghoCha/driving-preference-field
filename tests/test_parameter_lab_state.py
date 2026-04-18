from pathlib import Path

from driving_preference_field.config import FieldConfig, ProgressionConfig
from driving_preference_field.ui.parameter_lab.state import ParameterLabState


ROOT = Path(__file__).resolve().parents[1]


def test_parameter_lab_state_loads_default_case_and_reference_presets() -> None:
    state = ParameterLabState(repo_root=ROOT, case_path=ROOT / "cases/toy/straight_corridor.yaml")

    assert state.current_case_path.name == "straight_corridor.yaml"
    assert state.snapshot is not None
    assert state.default_context == state.working_context
    assert state.baseline_state.preset_name == "baseline__balanced_field"
    assert state.candidate_state.preset_name == "candidate__strong_longitudinal"

    baseline_descriptors, candidate_descriptors = state.grouped_preset_descriptors()
    assert any(descriptor.path.stem == "baseline__balanced_field" for descriptor in baseline_descriptors)
    assert any(descriptor.path.stem == "candidate__strong_longitudinal" for descriptor in candidate_descriptors)


def test_parameter_lab_state_marks_unsaved_and_saves_user_preset(tmp_path) -> None:
    state = ParameterLabState(repo_root=ROOT, case_path=ROOT / "cases/toy/straight_corridor.yaml")
    state.update_preset_root(tmp_path / "presets")

    updated = FieldConfig(
        progression=ProgressionConfig(longitudinal_gain=1.75),
        surface_tuning=state.baseline_config.surface_tuning,
    )
    state.update_side_config("baseline", updated)

    assert state.baseline_state.unsaved is True
    saved, message = state.save_preset_from_side("baseline", "user_baseline")

    assert saved is True
    assert message is None
    assert (state.preset_root / "user_baseline.yaml").exists()
    assert state.baseline_state.preset_name == "user_baseline"
    assert state.baseline_state.unsaved is False


def test_parameter_lab_state_copy_side_preserves_config_and_marks_target_unsaved() -> None:
    state = ParameterLabState(repo_root=ROOT, case_path=ROOT / "cases/toy/straight_corridor.yaml")

    state.copy_side("baseline", "candidate")

    assert state.candidate_config == state.baseline_config
    assert state.candidate_state.unsaved is True
    assert state.candidate_state.metadata["origin"] == "user"


def test_parameter_lab_state_lists_toy_cases_and_generic_fixtures() -> None:
    state = ParameterLabState(repo_root=ROOT, case_path=ROOT / "cases/toy/straight_corridor.yaml")

    available_names = {path.name for path in state.available_case_paths()}

    assert "straight_corridor.yaml" in available_names
    assert "straight_corridor_generic.yaml" in available_names
    assert "left_bend_drivable_only_generic.yaml" in available_names
    assert "circular_arc_drivable_only_generic.yaml" in available_names
    assert "full_circle_global_plan_generic.yaml" in available_names
    assert "split_branch_drivable_only_generic.yaml" not in available_names
