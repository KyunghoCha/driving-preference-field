from pathlib import Path

import numpy as np

from driving_preference_field.config import FieldConfig, ProgressionConfig
from driving_preference_field.contracts import QueryContext, QueryWindow, StateSample, TrajectorySample
from driving_preference_field.evaluator import evaluate_state, evaluate_trajectory
from driving_preference_field.field_runtime import build_field_runtime
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
    return FieldConfig(progression=ProgressionConfig(**payload))


def test_field_runtime_state_query_matches_evaluator_semantics() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    state = StateSample(x=4.7, y=2.0, yaw=1.0)

    runtime = build_field_runtime(snapshot, context, config=config)
    payload = runtime.query_state(state)
    result = evaluate_state(snapshot, context, state, config=config)

    assert payload.base_channels == result.base_preference_channels
    assert payload.soft_channels == result.soft_exception_channels
    assert payload.hard_flags == result.hard_violation_flags
    assert payload.diagnostics["progression_s_hat"] == result.diagnostics["progression_s_hat"]
    assert payload.diagnostics["progression_n_hat"] == result.diagnostics["progression_n_hat"]


def test_field_runtime_trajectory_query_matches_evaluator_ordering() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(longitudinal_gain=1.5)
    trajectory = TrajectorySample(
        states=(
            StateSample(x=1.0, y=0.0, yaw=0.0),
            StateSample(x=2.0, y=0.1, yaw=0.0),
            StateSample(x=3.0, y=0.1, yaw=0.0),
        )
    )

    runtime = build_field_runtime(snapshot, context, config=config)
    payload = runtime.query_trajectory(trajectory)
    result = evaluate_trajectory(snapshot, context, trajectory, config=config)

    assert payload.base_channels == result.trajectory_base_preference_channels
    assert payload.soft_channels == result.trajectory_soft_exception_channels
    assert payload.hard_flags == result.trajectory_hard_violation_flags
    assert payload.ordering_key == result.ordering_key


def test_field_runtime_debug_grid_exposes_progression_components() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    runtime = build_field_runtime(snapshot, context)

    x_coords = np.linspace(-0.5, 6.5, 8)
    y_coords = np.linspace(-1.5, 1.5, 6)
    grid = runtime.query_debug_grid(x_coords, y_coords)

    assert grid["progression_tilted"].shape == (6, 8)
    assert grid["progression_s_hat"].shape == (6, 8)
    assert grid["progression_n_hat"].shape == (6, 8)
    assert grid["progression_longitudinal_component"].shape == (6, 8)
    assert grid["progression_transverse_component"].shape == (6, 8)
    assert grid["progression_support_mod"].shape == (6, 8)
    assert grid["progression_alignment_mod"].shape == (6, 8)


def test_overlap_ordering_stays_stable_under_small_context_shift() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    shifted = QueryContext(
        semantic_snapshot=snapshot,
        ego_pose=StateSample(
            x=context.ego_pose.x + 0.25,
            y=context.ego_pose.y,
            yaw=context.ego_pose.yaw,
        ),
        local_window=QueryWindow(
            x_min=context.local_window.x_min + 0.25,
            x_max=context.local_window.x_max + 0.25,
            y_min=context.local_window.y_min,
            y_max=context.local_window.y_max,
        ),
        mode=context.mode,
        phase=context.phase,
    )
    config = _canonical_config(longitudinal_frame="ego_relative", lookahead_scale=0.25)
    center = StateSample(x=2.0, y=0.0, yaw=0.0)
    off_axis = StateSample(x=2.0, y=0.5, yaw=0.0)

    first_runtime = build_field_runtime(snapshot, context, config=config)
    second_runtime = build_field_runtime(snapshot, shifted, config=config)

    assert first_runtime.query_state(center).base_channels["progression_tilted"] > first_runtime.query_state(off_axis).base_channels["progression_tilted"]
    assert second_runtime.query_state(center).base_channels["progression_tilted"] > second_runtime.query_state(off_axis).base_channels["progression_tilted"]


def test_visible_endpoint_no_longer_creates_local_end_cap_peak() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(longitudinal_frame="local_absolute", longitudinal_gain=2.0)
    near_end = StateSample(x=5.8, y=0.0, yaw=0.0)
    visible_end = StateSample(x=6.0, y=0.0, yaw=0.0)
    beyond_end = StateSample(x=6.4, y=0.0, yaw=0.0)

    runtime = build_field_runtime(snapshot, context, config=config)
    near_score = runtime.query_state(near_end).base_channels["progression_tilted"]
    end_score = runtime.query_state(visible_end).base_channels["progression_tilted"]
    beyond_score = runtime.query_state(beyond_end).base_channels["progression_tilted"]

    assert end_score >= near_score
    assert beyond_score >= end_score - 0.05


def test_field_runtime_respects_zero_progression_support_ceiling() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(support_ceiling=0.0)
    runtime = build_field_runtime(snapshot, context, config=config)
    state = StateSample(x=4.0, y=0.0, yaw=0.0)

    assert runtime.query_state(state).base_channels["progression_tilted"] == 0.0
