from pathlib import Path

from driving_preference_field.config import (
    DEFAULT_FIELD_CONFIG,
    ComparisonPreset,
    FieldConfig,
    ProgressionConfig,
)
from driving_preference_field.evaluator import evaluate_state
from driving_preference_field.presets import load_preset, save_preset
from driving_preference_field.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_default_field_config_preserves_baseline_behavior() -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    snapshot, context = load_toy_snapshot(case_path)
    state = type(context.ego_pose)(x=4.8, y=2.8, yaw=1.2)

    implicit = evaluate_state(snapshot, context, state)
    explicit = evaluate_state(snapshot, context, state, config=DEFAULT_FIELD_CONFIG)

    assert explicit.base_preference_channels == implicit.base_preference_channels
    assert explicit.soft_exception_channels == implicit.soft_exception_channels
    assert explicit.hard_violation_flags == implicit.hard_violation_flags
    assert explicit.base_preference_total == implicit.base_preference_total
    assert explicit.soft_exception_total == implicit.soft_exception_total


def test_progression_config_change_only_affects_progression_channel() -> None:
    case_path = ROOT / "cases/toy/left_bend.yaml"
    snapshot, context = load_toy_snapshot(case_path)
    state = type(context.ego_pose)(x=4.8, y=2.8, yaw=1.2)

    baseline = evaluate_state(snapshot, context, state, config=DEFAULT_FIELD_CONFIG)
    candidate_config = FieldConfig(
        progression=ProgressionConfig(
            longitudinal_frame="ego_relative",
            longitudinal_family="linear",
            longitudinal_gain=2.0,
            lookahead_scale=0.4,
            longitudinal_shape=1.5,
            transverse_family="inverse",
            transverse_scale=1.4,
            transverse_shape=2.0,
            support_ceiling=0.9,
        ),
        interior_boundary=DEFAULT_FIELD_CONFIG.interior_boundary,
        continuity_branch=DEFAULT_FIELD_CONFIG.continuity_branch,
    )
    candidate = evaluate_state(snapshot, context, state, config=candidate_config)

    assert (
        candidate.base_preference_channels["progression_tilted"]
        != baseline.base_preference_channels["progression_tilted"]
    )
    assert (
        candidate.base_preference_channels["interior_boundary"]
        == baseline.base_preference_channels["interior_boundary"]
    )
    assert (
        candidate.base_preference_channels["continuity_branch"]
        == baseline.base_preference_channels["continuity_branch"]
    )
    assert candidate.soft_exception_channels == baseline.soft_exception_channels
    assert candidate.hard_violation_flags == baseline.hard_violation_flags


def test_comparison_preset_roundtrip(tmp_path) -> None:
    preset = ComparisonPreset(
        preset_name="candidate_v1",
        field_config=FieldConfig(
            progression=ProgressionConfig(
                longitudinal_frame="local_absolute",
                longitudinal_family="power",
                longitudinal_gain=1.5,
                lookahead_scale=0.45,
                longitudinal_shape=2.5,
                transverse_family="inverse",
                transverse_scale=1.2,
                transverse_shape=1.75,
                support_ceiling=0.8,
            ),
        ),
        note="roundtrip",
        metadata={"tag": "test"},
    )

    saved_path = save_preset(preset, tmp_path / "candidate_v1.yaml")
    loaded = load_preset(saved_path)

    assert loaded == preset
