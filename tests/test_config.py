from pathlib import Path

import pytest

from driving_preference_field.config import (
    DEFAULT_FIELD_CONFIG,
    ComparisonPreset,
    FieldConfig,
    ProgressionConfig,
    SurfaceTuningConfig,
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
    assert explicit.base_preference_total == implicit.base_preference_total


def test_progression_config_change_only_affects_progression_channel() -> None:
    case_path = ROOT / "cases/toy/left_bend.yaml"
    snapshot, context = load_toy_snapshot(case_path)
    state = type(context.ego_pose)(x=4.8, y=2.8, yaw=1.2)

    baseline = evaluate_state(snapshot, context, state, config=DEFAULT_FIELD_CONFIG)
    candidate_config = FieldConfig(
        progression=ProgressionConfig(
            longitudinal_frame="ego_relative",
            longitudinal_family="linear",
            longitudinal_peak=1.8,
            longitudinal_gain=2.0,
            lookahead_scale=0.4,
            longitudinal_shape=1.5,
            transverse_family="inverse",
            transverse_shape=2.0,
            support_ceiling=0.9,
        ),
    )
    candidate = evaluate_state(snapshot, context, state, config=candidate_config)

    assert (
        candidate.base_preference_channels["progression_tilted"]
        != baseline.base_preference_channels["progression_tilted"]
    )


def test_legacy_field_config_payload_ignores_removed_geometry_keys() -> None:
    config = FieldConfig.from_dict(
        {
            "progression": {"longitudinal_gain": 2.0},
            "interior_boundary": {"gain": 9.0},
            "continuity_branch": {"gain": 9.0},
        }
    )

    assert config.progression.longitudinal_gain == 2.0
    assert "interior_boundary" not in config.to_dict()
    assert "continuity_branch" not in config.to_dict()
    assert config.surface_tuning == SurfaceTuningConfig()


def test_field_config_roundtrip_preserves_surface_tuning() -> None:
    config = FieldConfig(
        progression=ProgressionConfig(longitudinal_gain=1.7),
        surface_tuning=SurfaceTuningConfig(
            anchor_spacing_m=0.35,
            spline_sample_density_m=0.08,
            spline_min_subdivisions=12,
            min_sigma_t=0.55,
            min_sigma_n=0.45,
            sigma_t_scale=0.5,
            sigma_n_scale=1.8,
            end_extension_m=3.0,
            support_base=0.9,
            support_range=0.1,
            alignment_base=0.85,
            alignment_range=0.15,
        ),
    )

    payload = config.to_dict()

    assert FieldConfig.from_dict(payload) == config
    assert payload["surface_tuning"]["anchor_spacing_m"] == 0.35
    assert payload["surface_tuning"]["spline_min_subdivisions"] == 12


def test_removed_transverse_handoff_surface_tuning_keys_raise() -> None:
    with pytest.raises(ValueError, match="transverse_handoff_temperature"):
        FieldConfig.from_dict({"surface_tuning": {"transverse_handoff_temperature": 0.08}})


def test_comparison_preset_roundtrip(tmp_path) -> None:
    preset = ComparisonPreset(
        preset_name="candidate_v1",
        field_config=FieldConfig(
            progression=ProgressionConfig(
                longitudinal_frame="local_absolute",
                longitudinal_family="power",
                longitudinal_peak=1.6,
                longitudinal_gain=1.5,
                lookahead_scale=0.45,
                longitudinal_shape=2.5,
                transverse_family="inverse",
                transverse_shape=1.75,
                support_ceiling=0.8,
            ),
            surface_tuning=SurfaceTuningConfig(anchor_spacing_m=0.3, end_extension_m=2.5),
        ),
        note="roundtrip",
        metadata={"tag": "test"},
    )

    saved_path = save_preset(preset, tmp_path / "candidate_v1.yaml")
    loaded = load_preset(saved_path)

    assert loaded == preset
