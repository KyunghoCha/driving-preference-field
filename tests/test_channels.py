from pathlib import Path

from driving_preference_field.config import FieldConfig, ProgressionConfig
from driving_preference_field.channels import (
    progression_tilted,
    progression_tilted_details,
)
from driving_preference_field.contracts import StateSample
from driving_preference_field.presets import load_preset
from driving_preference_field.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def _canonical_config(**kwargs) -> FieldConfig:
    payload = {
        "longitudinal_frame": "local_absolute",
        "longitudinal_family": "linear",
        "longitudinal_gain": 1.0,
        "lookahead_scale": 0.35,
        "longitudinal_shape": 1.0,
        "transverse_family": "exponential",
        "transverse_scale": 1.0,
        "transverse_shape": 1.0,
        "support_ceiling": 1.0,
    }
    payload.update(kwargs)
    progression = ProgressionConfig(**payload)
    return FieldConfig(progression=progression)


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


def test_progression_transverse_scale_controls_off_axis_falloff() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    offset = StateSample(x=4.4, y=0.8, yaw=0.0)
    narrow = _canonical_config(transverse_scale=0.5)
    wide = _canonical_config(transverse_scale=2.0)

    assert progression_tilted(snapshot, context, offset, config=wide) > progression_tilted(
        snapshot,
        context,
        offset,
        config=narrow,
    )


def test_progression_transverse_shape_controls_off_axis_contrast() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    offset = StateSample(x=4.4, y=1.6, yaw=0.0)
    soft = _canonical_config(transverse_family="power", transverse_shape=1.0)
    sharp = _canonical_config(transverse_family="power", transverse_shape=3.0)

    assert progression_tilted(snapshot, context, offset, config=soft) > progression_tilted(
        snapshot,
        context,
        offset,
        config=sharp,
    )


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
        transverse_scale=1.0,
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


def test_ego_relative_longitudinal_frame_strengthens_ahead_bias() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    local_absolute = _canonical_config(
        longitudinal_frame="local_absolute",
        longitudinal_family="linear",
        longitudinal_gain=1.0,
        transverse_family="exponential",
        transverse_scale=1.0,
        transverse_shape=1.0,
    )
    ego_relative = _canonical_config(
        longitudinal_frame="ego_relative",
        longitudinal_family="linear",
        longitudinal_gain=1.0,
        lookahead_scale=0.25,
        transverse_family="exponential",
        transverse_scale=1.0,
        transverse_shape=1.0,
    )
    behind_center = StateSample(x=0.2, y=0.0, yaw=0.0)
    slightly_ahead_off_axis = StateSample(x=2.0, y=0.2, yaw=0.0)

    local_behind = progression_tilted(snapshot, context, behind_center, config=local_absolute)
    local_ahead = progression_tilted(snapshot, context, slightly_ahead_off_axis, config=local_absolute)
    ego_behind = progression_tilted(snapshot, context, behind_center, config=ego_relative)
    ego_ahead = progression_tilted(snapshot, context, slightly_ahead_off_axis, config=ego_relative)

    assert local_ahead > local_behind
    assert ego_ahead > ego_behind
    assert (ego_ahead - ego_behind) > (local_ahead - local_behind)


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


def test_left_bend_projection_coordinates_keep_centerline_transverse_stable() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    center_samples = (
        StateSample(x=3.0, y=0.0, yaw=0.0),
        StateSample(x=4.6, y=1.6, yaw=1.1),
        StateSample(x=5.0, y=3.5, yaw=1.57),
    )
    outer_samples = (
        StateSample(x=3.0, y=-0.8, yaw=0.0),
        StateSample(x=5.1, y=0.9, yaw=1.1),
        StateSample(x=5.8, y=3.5, yaw=1.57),
    )

    center_transverse = []
    for center_state, outer_state in zip(center_samples, outer_samples, strict=True):
        center_details = progression_tilted_details(snapshot, context, center_state, config=config)
        outer_details = progression_tilted_details(snapshot, context, outer_state, config=config)
        center_transverse.append(center_details["transverse_component"])
        assert center_details["score"] > outer_details["score"]

    assert max(center_transverse) - min(center_transverse) <= 0.18


def test_split_branch_centers_beat_midpoint_after_divergence() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/split_branch.yaml")
    config = _canonical_config()
    upper_branch = StateSample(x=5.2, y=1.4, yaw=0.55)
    lower_branch = StateSample(x=5.2, y=-1.4, yaw=-0.55)
    midpoint = StateSample(x=5.2, y=0.0, yaw=0.0)
    divergence_onset = StateSample(x=3.8, y=0.0, yaw=0.0)

    upper_score = progression_tilted(snapshot, context, upper_branch, config=config)
    lower_score = progression_tilted(snapshot, context, lower_branch, config=config)
    midpoint_score = progression_tilted(snapshot, context, midpoint, config=config)

    assert upper_score - midpoint_score >= 0.15
    assert lower_score - midpoint_score >= 0.15
    assert progression_tilted(snapshot, context, divergence_onset, config=config) > 0.0


def test_merge_like_patch_exterior_transverse_handoff_is_smooth() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    config = _canonical_config()
    shared_suffix = progression_tilted_details(
        snapshot,
        context,
        StateSample(x=4.2, y=0.0, yaw=0.0),
        config=config,
    )
    assert shared_suffix["score"] > 0.0

    upper_exterior = (
        StateSample(x=1.2, y=1.35, yaw=-0.35),
        StateSample(x=2.2, y=0.95, yaw=-0.25),
        StateSample(x=3.2, y=0.55, yaw=-0.15),
    )
    lower_exterior = tuple(
        StateSample(x=state.x, y=-state.y, yaw=-state.yaw) for state in upper_exterior
    )

    upper_transverse = [
        progression_tilted_details(snapshot, context, state, config=config)["transverse_component"]
        for state in upper_exterior
    ]
    lower_transverse = [
        progression_tilted_details(snapshot, context, state, config=config)["transverse_component"]
        for state in lower_exterior
    ]

    for first, second in zip(upper_transverse, upper_transverse[1:]):
        assert abs(second - first) <= 0.18
    for first, second in zip(lower_transverse, lower_transverse[1:]):
        assert abs(second - first) <= 0.18


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
        transverse_scale=1.0,
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
