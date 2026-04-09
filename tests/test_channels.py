from pathlib import Path

from driving_preference_field.config import FieldConfig, ProgressionConfig
from driving_preference_field.channels import (
    continuity_branch,
    interior_boundary,
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


def test_interior_boundary_prefers_interior_over_boundary() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    interior = StateSample(x=2.0, y=0.0, yaw=0.0)
    near_boundary = StateSample(x=2.0, y=0.9, yaw=0.0)

    assert interior_boundary(snapshot, context, interior) > interior_boundary(snapshot, context, near_boundary)


def test_continuity_branch_distinguishes_branch_alternatives() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/split_branch.yaml")
    upper = StateSample(x=5.2, y=1.4, yaw=0.55)
    wrong_for_upper = StateSample(x=5.2, y=1.4, yaw=-0.55)
    lower = StateSample(x=5.2, y=-1.4, yaw=-0.55)

    assert continuity_branch(snapshot, context, upper) > continuity_branch(snapshot, context, wrong_for_upper)
    assert continuity_branch(snapshot, context, lower) > 0.0


def test_progression_tilted_is_bounded_for_weak_sensor_patch() -> None:
    weak_snapshot, weak_context = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_open.yaml")
    weak_state = StateSample(x=1.8, y=0.0, yaw=0.0)
    weak_details = progression_tilted_details(weak_snapshot, weak_context, weak_state)

    assert 0.0 < weak_details["score"] < 2.0
    assert weak_details["support_mod"] < 1.0


def test_interior_boundary_prefers_center_in_narrow_patch() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_narrow.yaml")
    center = StateSample(x=1.8, y=0.0, yaw=0.0)
    edge = StateSample(x=1.8, y=0.28, yaw=0.0)

    assert interior_boundary(snapshot, context, center) > interior_boundary(snapshot, context, edge)


def test_continuity_branch_reads_merge_like_preference() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    aligned = StateSample(x=3.4, y=0.25, yaw=-0.2)
    misaligned = StateSample(x=3.4, y=0.25, yaw=1.2)

    assert continuity_branch(snapshot, context, aligned) > continuity_branch(snapshot, context, misaligned)


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
    branch_gap = StateSample(x=5.2, y=0.0, yaw=0.55)
    outer_upper = StateSample(x=5.2, y=2.2, yaw=0.55)

    assert progression_tilted(snapshot, context, upper_branch, config=config) > progression_tilted(
        snapshot,
        context,
        outer_upper,
        config=config,
    )
    assert progression_tilted(snapshot, context, branch_gap, config=config) > 0.0


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


def test_longitudinal_frame_choice_changes_point_ordering() -> None:
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
