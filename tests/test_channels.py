from pathlib import Path

from local_reference_path_cost.config import FieldConfig, ProgressionConfig, SurfaceTuningConfig
from local_reference_path_cost.channels import (
    progression_tilted,
    progression_tilted_details,
)
from local_reference_path_cost.contracts import StateSample
from local_reference_path_cost.presets import load_preset
from local_reference_path_cost.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def _canonical_config(*, surface_tuning: SurfaceTuningConfig | None = None, **kwargs) -> FieldConfig:
    payload = {
        "longitudinal_frame": "local_absolute",
        "longitudinal_family": "linear",
        "longitudinal_gain": 1.0,
        "lookahead_scale": 0.35,
        "longitudinal_shape": 1.0,
        "transverse_family": "exponential",
        "transverse_peak": 1.0,
        "transverse_shape": 1.0,
        "transverse_falloff": 0.0,
        "support_ceiling": 1.0,
    }
    payload.update(kwargs)
    progression = ProgressionConfig(**payload)
    return FieldConfig(progression=progression, surface_tuning=surface_tuning or SurfaceTuningConfig())


def test_progression_tilted_prefers_forward_alignment() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    forward = StateSample(x=2.0, y=0.0, yaw=0.0)
    reverse = StateSample(x=2.0, y=0.0, yaw=3.141592653589793)

    assert progression_tilted(snapshot, context, forward) > progression_tilted(snapshot, context, reverse)


def test_progression_tilted_is_bounded_for_weak_sensor_patch() -> None:
    weak_snapshot, weak_context = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_open.yaml")
    weak_state = StateSample(x=1.8, y=0.0, yaw=0.0)
    weak_details = progression_tilted_details(weak_snapshot, weak_context, weak_state)

    assert 0.0 < weak_details["score"] < 2.0
    assert weak_details["support_mod"] < 1.0


def test_progression_longitudinal_gain_extends_score_along_axis() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    later = StateSample(x=4.4, y=0.0, yaw=0.0)
    weak = _canonical_config(longitudinal_gain=0.5)
    strong = _canonical_config(longitudinal_gain=2.0)

    assert progression_tilted(snapshot, context, later, config=strong) > progression_tilted(
        snapshot,
        context,
        later,
        config=weak,
    )


def test_progression_transverse_is_center_high_with_same_longitudinal_slice() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(longitudinal_frame="local_absolute", longitudinal_gain=1.0)
    center = StateSample(x=3.0, y=0.0, yaw=0.0)
    off_axis = StateSample(x=3.0, y=0.6, yaw=0.0)

    assert progression_tilted(snapshot, context, center, config=config) > progression_tilted(
        snapshot,
        context,
        off_axis,
        config=config,
    )


def test_legacy_transverse_scale_no_longer_changes_off_axis_falloff() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    offset = StateSample(x=4.4, y=0.8, yaw=0.0)
    narrow = _canonical_config(transverse_scale=0.5)
    wide = _canonical_config(transverse_scale=2.0)

    assert progression_tilted(snapshot, context, offset, config=wide) == progression_tilted(
        snapshot,
        context,
        offset,
        config=narrow,
    )


def test_progression_transverse_peak_scales_center_ceiling() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    center = StateSample(x=4.4, y=0.0, yaw=0.0)
    low_peak = _canonical_config(transverse_family="exponential", transverse_peak=1.0, longitudinal_gain=0.0)
    high_peak = _canonical_config(transverse_family="exponential", transverse_peak=3.0, longitudinal_gain=0.0)

    assert progression_tilted(snapshot, context, center, config=high_peak) > progression_tilted(
        snapshot,
        context,
        center,
        config=low_peak,
    )


def test_progression_transverse_shape_controls_core_flatness() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    near_axis = StateSample(x=4.4, y=0.35, yaw=0.0)
    pointy = _canonical_config(transverse_family="exponential", transverse_shape=0.6, longitudinal_gain=0.0)
    broad = _canonical_config(transverse_family="exponential", transverse_shape=2.0, longitudinal_gain=0.0)

    assert progression_tilted(snapshot, context, near_axis, config=broad) > progression_tilted(
        snapshot,
        context,
        near_axis,
        config=pointy,
    )


def test_progression_transverse_falloff_controls_outer_tail() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    far_offset = StateSample(x=4.4, y=1.6, yaw=0.0)
    low_falloff = _canonical_config(transverse_family="exponential", transverse_falloff=0.0, longitudinal_gain=0.0)
    high_falloff = _canonical_config(transverse_family="exponential", transverse_falloff=3.0, longitudinal_gain=0.0)

    assert progression_tilted(snapshot, context, far_offset, config=low_falloff) > progression_tilted(
        snapshot,
        context,
        far_offset,
        config=high_falloff,
    )


def test_progression_transverse_linear_family_produces_linear_flanks() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(
        transverse_family="linear",
        transverse_peak=2.0,
        transverse_shape=1.0,
        transverse_falloff=0.0,
        longitudinal_gain=0.0,
    )
    center = progression_tilted_details(snapshot, context, StateSample(x=4.4, y=0.0, yaw=0.0), config=config)
    mid = progression_tilted_details(snapshot, context, StateSample(x=4.4, y=0.5, yaw=0.0), config=config)
    edge = progression_tilted_details(snapshot, context, StateSample(x=4.4, y=1.0, yaw=0.0), config=config)

    assert center["transverse_term"] == 2.0
    assert abs(mid["transverse_term"] - 1.0) < 1e-6
    assert abs(edge["transverse_term"]) < 1e-6


def test_progression_follows_bend_guide_better_than_off_curve_point() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    on_curve = StateSample(x=5.0, y=3.5, yaw=1.57)
    off_curve = StateSample(x=4.0, y=3.5, yaw=1.57)

    assert progression_tilted(snapshot, context, on_curve, config=config) > progression_tilted(
        snapshot,
        context,
        off_curve,
        config=config,
    )


def test_progression_split_branch_gap_is_filled_without_hole() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/split_branch.yaml")
    config = _canonical_config()
    upper_branch = StateSample(x=5.2, y=1.4, yaw=0.55)
    lower_branch = StateSample(x=5.2, y=-1.4, yaw=-0.55)
    branch_gap = StateSample(x=5.2, y=0.0, yaw=0.55)
    outer_upper = StateSample(x=5.2, y=2.2, yaw=0.55)
    divergence_onset = StateSample(x=3.8, y=0.0, yaw=0.0)

    assert progression_tilted(snapshot, context, upper_branch, config=config) > progression_tilted(
        snapshot,
        context,
        outer_upper,
        config=config,
    )
    assert progression_tilted(snapshot, context, upper_branch, config=config) > progression_tilted(
        snapshot,
        context,
        branch_gap,
        config=config,
    )
    assert progression_tilted(snapshot, context, lower_branch, config=config) > progression_tilted(
        snapshot,
        context,
        branch_gap,
        config=config,
    )
    assert progression_tilted(snapshot, context, branch_gap, config=config) > 0.0
    assert progression_tilted(snapshot, context, divergence_onset, config=config) > 0.0


def test_strong_longitudinal_can_outweigh_near_center_preference() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(
        longitudinal_frame="local_absolute",
        longitudinal_family="linear",
        longitudinal_gain=4.0,
        transverse_family="exponential",
        transverse_shape=1.0,
    )
    near_center = StateSample(x=1.0, y=0.0, yaw=0.0)
    farther_off_axis = StateSample(x=5.0, y=0.8, yaw=0.0)

    assert progression_tilted(snapshot, context, farther_off_axis, config=config) > progression_tilted(
        snapshot,
        context,
        near_center,
        config=config,
    )


def test_longitudinal_frame_choice_changes_point_ordering() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    local_absolute = _canonical_config(
        longitudinal_frame="local_absolute",
        longitudinal_family="linear",
        longitudinal_gain=1.0,
        transverse_family="exponential",
        transverse_shape=1.0,
    )
    ego_relative = _canonical_config(
        longitudinal_frame="ego_relative",
        longitudinal_family="linear",
        longitudinal_gain=1.0,
        lookahead_scale=0.25,
        transverse_family="exponential",
        transverse_shape=1.0,
    )
    behind_center = StateSample(x=0.2, y=0.0, yaw=0.0)
    slightly_ahead_off_axis = StateSample(x=2.0, y=0.2, yaw=0.0)

    assert progression_tilted(snapshot, context, behind_center, config=local_absolute) > progression_tilted(
        snapshot,
        context,
        slightly_ahead_off_axis,
        config=local_absolute,
    )
    assert progression_tilted(snapshot, context, slightly_ahead_off_axis, config=ego_relative) > progression_tilted(
        snapshot,
        context,
        behind_center,
        config=ego_relative,
    )


def test_progression_bend_line_stays_continuous_without_hard_reset() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    values = [
        progression_tilted(
            snapshot,
            context,
            StateSample(x=x_value, y=2.4, yaw=1.1),
            config=config,
        )
        for x_value in (4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2)
    ]

    assert min(values) > 0.0
    assert max(abs(values[index + 1] - values[index]) for index in range(len(values) - 1)) < 0.25


def test_progression_merge_midline_is_nonzero_continuous_surface() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    config = _canonical_config()
    midline = StateSample(x=3.2, y=0.0, yaw=0.0)
    upper = StateSample(x=3.2, y=0.25, yaw=-0.2)
    lower = StateSample(x=3.2, y=-0.25, yaw=0.2)

    assert progression_tilted(snapshot, context, midline, config=config) > 0.0
    assert progression_tilted(snapshot, context, upper, config=config) > 0.0
    assert progression_tilted(snapshot, context, lower, config=config) > 0.0


def test_surface_tuning_changes_progress_blend_without_changing_exact_transverse_term() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    state = StateSample(x=2.6, y=-0.1, yaw=0.2)
    baseline = progression_tilted_details(snapshot, context, state, config=_canonical_config())
    tuned = progression_tilted_details(
        snapshot,
        context,
        state,
        config=_canonical_config(
            surface_tuning=SurfaceTuningConfig(
                anchor_spacing_m=0.1,
                sigma_t_scale=0.6,
            )
        ),
    )

    assert set(tuned) == set(baseline)
    assert tuned["s_hat"] != baseline["s_hat"]
    assert tuned["transverse_term"] == baseline["transverse_term"]
    assert tuned["center_distance"] == baseline["center_distance"]




def test_progression_u_turn_keeps_hairpin_continuity_and_center_high_return_leg() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    hairpin_apex = StateSample(x=5.0, y=1.8, yaw=1.57)
    return_center = StateSample(x=2.0, y=3.2, yaw=3.141592653589793)
    return_off_axis = StateSample(x=2.0, y=2.5, yaw=3.141592653589793)

    assert progression_tilted(snapshot, context, hairpin_apex, config=config) > 0.0
    assert progression_tilted(snapshot, context, return_center, config=config) > progression_tilted(
        snapshot,
        context,
        return_off_axis,
        config=config,
    )


def test_strong_longitudinal_can_prefer_farther_return_leg_in_u_turn() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    config = _canonical_config(
        longitudinal_frame="local_absolute",
        longitudinal_family="linear",
        longitudinal_gain=3.0,
        transverse_family="exponential",
        transverse_shape=1.0,
    )
    near_entry_center = StateSample(x=1.0, y=0.0, yaw=0.0)
    farther_return = StateSample(x=2.0, y=3.2, yaw=3.141592653589793)

    assert progression_tilted(snapshot, context, farther_return, config=config) > progression_tilted(
        snapshot,
        context,
        near_entry_center,
        config=config,
    )


def test_many_small_guides_u_turn_keeps_hairpin_continuity_and_center_high_return_leg() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn_many_small_progression_guides.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    hairpin_apex = StateSample(x=5.0, y=1.8, yaw=1.57)
    seam_probe = StateSample(x=4.65, y=0.35, yaw=0.4)
    return_center = StateSample(x=2.0, y=3.2, yaw=3.141592653589793)
    return_off_axis = StateSample(x=2.0, y=2.5, yaw=3.141592653589793)

    assert progression_tilted(snapshot, context, hairpin_apex, config=config) > 0.0
    assert progression_tilted(snapshot, context, seam_probe, config=config) > 0.0
    assert progression_tilted(snapshot, context, return_center, config=config) > progression_tilted(
        snapshot,
        context,
        return_off_axis,
        config=config,
    )


def test_many_small_guides_u_turn_stays_close_to_single_guide_u_turn() -> None:
    reference_snapshot, reference_context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    fragmented_snapshot, fragmented_context = load_toy_snapshot(
        ROOT / "cases/toy/u_turn_many_small_progression_guides.yaml"
    )
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    probe_states = (
        StateSample(x=3.0, y=0.0, yaw=0.0),
        StateSample(x=4.85, y=0.6, yaw=0.8),
        StateSample(x=5.0, y=1.8, yaw=1.57),
        StateSample(x=2.0, y=3.2, yaw=3.141592653589793),
    )

    for state in probe_states:
        reference = progression_tilted(reference_snapshot, reference_context, state, config=config)
        fragmented = progression_tilted(fragmented_snapshot, fragmented_context, state, config=config)
        assert abs(fragmented - reference) <= max(0.08, 0.15 * abs(reference))


def test_no_progression_reference_preset_disables_progression_channel() -> None:
    preset = load_preset(ROOT / "presets/lab/baseline__no_progression.yaml")
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    state = StateSample(x=4.4, y=0.0, yaw=0.0)

    assert progression_tilted(snapshot, context, state, config=preset.field_config) == 0.0


def test_two_lane_straight_creates_lane_centers_with_valley_between_them() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/two_lane_straight.yaml")
    config = _canonical_config(longitudinal_frame="local_absolute", longitudinal_gain=1.0)
    lower_lane = StateSample(x=3.0, y=-0.6, yaw=0.0)
    midpoint = StateSample(x=3.0, y=0.0, yaw=0.0)
    upper_lane = StateSample(x=3.0, y=0.6, yaw=0.0)
    outer_edge = StateSample(x=3.0, y=1.8, yaw=0.0)

    lower_score = progression_tilted(snapshot, context, lower_lane, config=config)
    midpoint_score = progression_tilted(snapshot, context, midpoint, config=config)
    upper_score = progression_tilted(snapshot, context, upper_lane, config=config)
    outer_score = progression_tilted(snapshot, context, outer_edge, config=config)

    assert lower_score > midpoint_score > outer_score
    assert upper_score > midpoint_score > outer_score
