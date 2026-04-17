from pathlib import Path

import numpy as np
import pytest

from driving_preference_field.config import FieldConfig, ProgressionConfig, SurfaceTuningConfig
from driving_preference_field.contracts import QueryContext, QueryWindow, StateSample, TrajectorySample
from driving_preference_field.evaluator import evaluate_state, evaluate_trajectory
from driving_preference_field.field_runtime import FieldRuntime, build_field_runtime
from driving_preference_field.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def _canonical_config(*, surface_tuning: SurfaceTuningConfig | None = None, **kwargs) -> FieldConfig:
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
    return FieldConfig(
        progression=ProgressionConfig(**payload),
        surface_tuning=surface_tuning or SurfaceTuningConfig(),
    )


def test_field_runtime_state_query_matches_evaluator_semantics() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    state = StateSample(x=4.7, y=2.0, yaw=1.0)

    runtime = build_field_runtime(snapshot, context, config=config)
    payload = runtime.query_state(state)
    result = evaluate_state(snapshot, context, state, config=config)

    assert payload.base_channels == result.base_preference_channels
    assert payload.diagnostics["progression_s_hat"] == result.diagnostics["progression_s_hat"]
    assert payload.diagnostics["progression_n_hat"] == result.diagnostics["progression_n_hat"]


def test_field_runtime_anchor_count_diagnostics_distinguish_total_and_effective_counts() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    runtime = build_field_runtime(snapshot, context)
    state = StateSample(x=4.7, y=2.0, yaw=1.0)

    payload = runtime.query_state(state)

    assert "progression_anchor_count" in payload.diagnostics
    assert "progression_effective_anchor_count" in payload.diagnostics
    assert payload.diagnostics["progression_anchor_count"] >= 0
    assert 0 <= payload.diagnostics["progression_effective_anchor_count"] <= payload.diagnostics["progression_anchor_count"]


def test_field_runtime_cache_does_not_create_semantic_drift() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    state = StateSample(x=4.7, y=2.0, yaw=1.0)

    first_runtime = build_field_runtime(snapshot, context, config=config)
    second_runtime = build_field_runtime(snapshot, context, config=config)

    first_payload = first_runtime.query_state(state)
    second_payload = second_runtime.query_state(state)

    assert first_payload.base_channels == second_payload.base_channels
    assert first_payload.diagnostics["progression_s_hat"] == second_payload.diagnostics["progression_s_hat"]
    assert first_payload.diagnostics["progression_n_hat"] == second_payload.diagnostics["progression_n_hat"]


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


def test_field_runtime_public_contract_is_locked_for_late_phase4() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    runtime = build_field_runtime(snapshot, context)

    assert isinstance(runtime, FieldRuntime)
    assert callable(build_field_runtime)
    assert callable(runtime.query_state)
    assert callable(runtime.query_trajectory)
    assert callable(runtime.query_progression_points)
    assert callable(runtime.query_progression_trajectories)
    assert callable(runtime.query_debug_grid)


def test_field_runtime_batched_progression_points_match_state_queries() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    runtime = build_field_runtime(snapshot, context)
    xs = np.asarray([4.7, 5.1, 5.5], dtype=float)
    ys = np.asarray([2.0, 2.4, 2.8], dtype=float)
    yaws = np.asarray([1.0, 1.0, 1.0], dtype=float)

    batched = runtime.query_progression_points(xs, ys, yaws)

    for index, (x, y, yaw) in enumerate(zip(xs, ys, yaws)):
        state = StateSample(x=float(x), y=float(y), yaw=float(yaw))
        single = runtime.query_state(state)
        assert batched["progression_tilted"][index] == pytest.approx(single.base_channels["progression_tilted"])
        assert batched["progression_s_hat"][index] == pytest.approx(single.diagnostics["progression_s_hat"])
        assert batched["progression_n_hat"][index] == pytest.approx(single.diagnostics["progression_n_hat"])


def test_field_runtime_batched_progression_trajectories_match_trajectory_sum() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    runtime = build_field_runtime(snapshot, context)
    trajectories_xy = np.asarray(
        [
            [[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]],
            [[1.0, 0.4], [2.0, 0.4], [3.0, 0.4]],
        ],
        dtype=float,
    )
    batched = runtime.query_progression_trajectories(trajectories_xy)
    center_trajectory = TrajectorySample(
        states=tuple(StateSample(x=float(x), y=float(y), yaw=0.0) for x, y in trajectories_xy[0])
    )
    off_axis_trajectory = TrajectorySample(
        states=tuple(StateSample(x=float(x), y=float(y), yaw=0.0) for x, y in trajectories_xy[1])
    )

    center_result = runtime.query_trajectory(center_trajectory)
    off_axis_result = runtime.query_trajectory(off_axis_trajectory)

    assert float(np.sum(batched["progression_tilted"][0])) == pytest.approx(center_result.base_channels["progression_tilted"])
    assert float(np.sum(batched["progression_tilted"][1])) == pytest.approx(off_axis_result.base_channels["progression_tilted"])


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


def test_left_bend_overlap_ordering_stays_stable_under_small_context_shift() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    shifted = QueryContext(
        semantic_snapshot=snapshot,
        ego_pose=StateSample(
            x=context.ego_pose.x + 0.15,
            y=context.ego_pose.y + 0.10,
            yaw=context.ego_pose.yaw,
        ),
        local_window=QueryWindow(
            x_min=context.local_window.x_min + 0.15,
            x_max=context.local_window.x_max + 0.15,
            y_min=context.local_window.y_min + 0.10,
            y_max=context.local_window.y_max + 0.10,
        ),
        mode=context.mode,
        phase=context.phase,
    )
    config = _canonical_config(longitudinal_family="tanh", longitudinal_shape=2.0)
    on_curve = StateSample(x=4.8, y=3.1, yaw=1.2)
    off_curve = StateSample(x=4.1, y=3.1, yaw=1.2)

    first_runtime = build_field_runtime(snapshot, context, config=config)
    second_runtime = build_field_runtime(snapshot, shifted, config=config)

    assert first_runtime.query_state(on_curve).base_channels["progression_tilted"] > first_runtime.query_state(off_curve).base_channels["progression_tilted"]
    assert second_runtime.query_state(on_curve).base_channels["progression_tilted"] > second_runtime.query_state(off_curve).base_channels["progression_tilted"]


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


def test_u_turn_visible_endpoint_does_not_create_fake_end_cap_on_return_leg() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    config = _canonical_config(longitudinal_frame="local_absolute", longitudinal_gain=2.0)
    near_visible_return_end = StateSample(x=0.9, y=3.2, yaw=3.141592653589793)
    visible_return_end = StateSample(x=0.4, y=3.2, yaw=3.141592653589793)
    beyond_visible_return_end = StateSample(x=0.0, y=3.2, yaw=3.141592653589793)

    runtime = build_field_runtime(snapshot, context, config=config)
    near_score = runtime.query_state(near_visible_return_end).base_channels["progression_tilted"]
    end_score = runtime.query_state(visible_return_end).base_channels["progression_tilted"]
    beyond_score = runtime.query_state(beyond_visible_return_end).base_channels["progression_tilted"]

    assert end_score >= near_score
    assert beyond_score >= end_score - 0.05


def test_field_runtime_respects_zero_progression_support_ceiling() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    config = _canonical_config(support_ceiling=0.0)
    runtime = build_field_runtime(snapshot, context, config=config)
    state = StateSample(x=4.0, y=0.0, yaw=0.0)

    assert runtime.query_state(state).base_channels["progression_tilted"] == 0.0


def test_field_runtime_default_surface_tuning_matches_implicit_default() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    runtime = build_field_runtime(snapshot, context)
    explicit = build_field_runtime(snapshot, context, config=FieldConfig())
    state = StateSample(x=4.7, y=2.0, yaw=1.0)

    implicit_payload = runtime.query_state(state)
    explicit_payload = explicit.query_state(state)

    assert implicit_payload.base_channels == explicit_payload.base_channels
    assert implicit_payload.diagnostics["progression_transverse_component"] == pytest.approx(
        explicit_payload.diagnostics["progression_transverse_component"]
    )


def test_field_runtime_surface_tuning_change_propagates_into_surface_output() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/split_branch.yaml")
    state = StateSample(x=3.4, y=0.1, yaw=0.55)
    baseline = build_field_runtime(snapshot, context, config=_canonical_config())
    candidate = build_field_runtime(
        snapshot,
        context,
        config=_canonical_config(
            surface_tuning=SurfaceTuningConfig(
                sigma_n_scale=2.2,
                alignment_range=0.12,
            )
        ),
    )

    baseline_payload = baseline.query_state(state)
    candidate_payload = candidate.query_state(state)

    assert candidate_payload.diagnostics["field_config"]["surface_tuning"]["sigma_n_scale"] == 2.2
    assert candidate_payload.diagnostics["progression_transverse_component"] != pytest.approx(
        baseline_payload.diagnostics["progression_transverse_component"]
    )


def test_field_runtime_transverse_component_matches_score_term() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    config = _canonical_config(
        longitudinal_family="tanh",
        longitudinal_shape=2.0,
        longitudinal_gain=1.4,
    )
    runtime = build_field_runtime(snapshot, context, config=config)
    payload = runtime.query_state(StateSample(x=4.8, y=3.0, yaw=1.2))

    support_alignment = (
        payload.diagnostics["progression_support_mod"] * payload.diagnostics["progression_alignment_mod"]
    )
    assert support_alignment > 0.0

    reconstructed_transverse = (
        payload.base_channels["progression_tilted"] / support_alignment
        - config.progression.longitudinal_gain * payload.diagnostics["progression_longitudinal_component"]
    )

    assert payload.diagnostics["progression_transverse_component"] == pytest.approx(reconstructed_transverse)
