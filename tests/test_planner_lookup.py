from pathlib import Path

import numpy as np

from driving_preference_field.config import FieldConfig, ProgressionConfig, SurfaceTuningConfig
from driving_preference_field.contracts import Point2
from driving_preference_field.field_runtime import build_field_runtime
from driving_preference_field.planner_lookup import (
    build_progression_lookup,
    clear_progression_lookup_cache,
    query_progression_lookup_points,
    query_progression_lookup_trajectories,
)
from driving_preference_field.raster import sample_local_raster
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


def test_progression_lookup_reuses_scene_cache_for_same_inputs() -> None:
    clear_progression_lookup_cache()
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    config = _canonical_config()

    first = build_progression_lookup(snapshot, context, config=config)
    second = build_progression_lookup(snapshot, context, config=config)
    different_spacing = build_progression_lookup(snapshot, context, config=config, grid_spacing_m=0.20)

    assert first is second
    assert first.cache_key == second.cache_key
    assert different_spacing is not first
    assert different_spacing.cache_key != first.cache_key


def test_progression_lookup_can_force_cold_build_without_cache_reuse() -> None:
    clear_progression_lookup_cache()
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    config = _canonical_config()

    cold_first = build_progression_lookup(snapshot, context, config=config, use_cache=False)
    cold_second = build_progression_lookup(snapshot, context, config=config, use_cache=False)
    cached = build_progression_lookup(snapshot, context, config=config)

    assert cold_first is not cold_second
    assert cold_first.cache_key == cold_second.cache_key == cached.cache_key
    assert cached is not cold_first
    assert cached is not cold_second


def test_progression_lookup_query_matches_stored_grid_on_grid_nodes() -> None:
    clear_progression_lookup_cache()
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    prepared = build_progression_lookup(snapshot, context)

    grid_x, grid_y = np.meshgrid(prepared.x_coords, prepared.y_coords)
    xy_points = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    sampled = query_progression_lookup_points(prepared, xy_points).reshape(prepared.progression_tilted.shape)

    assert np.allclose(sampled, prepared.progression_tilted)


def test_progression_score_grid_matches_debug_grid_score_channel() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    runtime = build_field_runtime(snapshot, context)
    x_coords = np.linspace(context.local_window.x_min, context.local_window.x_max, 41)
    y_coords = np.linspace(context.local_window.y_min, context.local_window.y_max, 33)

    score_only = runtime.query_progression_score_grid(x_coords, y_coords)
    debug_score = runtime.query_debug_grid(x_coords, y_coords)["progression_tilted"]

    assert np.allclose(score_only, debug_score)


def test_progression_lookup_build_uses_exact_score_grid_oracle() -> None:
    clear_progression_lookup_cache()
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    runtime = build_field_runtime(snapshot, context)
    prepared = build_progression_lookup(snapshot, context, grid_spacing_m=0.2, use_cache=False)

    exact_score = runtime.query_progression_score_grid(prepared.x_coords, prepared.y_coords)

    assert np.allclose(prepared.progression_tilted, exact_score)


def test_progression_lookup_trajectory_query_preserves_shape_and_dtype() -> None:
    clear_progression_lookup_cache()
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    prepared = build_progression_lookup(snapshot, context)
    trajectories_xy = np.asarray(
        [
            [[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]],
            [[1.0, 0.4], [2.0, 0.4], [3.0, 0.4]],
        ],
        dtype=float,
    )

    scores = query_progression_lookup_trajectories(prepared, trajectories_xy)

    assert scores.shape == (2, 3)
    assert scores.dtype == np.float64


def test_progression_lookup_stays_close_to_exact_scores_on_common_cases() -> None:
    clear_progression_lookup_cache()
    cases = (
        "straight_corridor",
        "left_bend",
        "split_branch",
        "u_turn",
        "u_turn_many_small_progression_guides",
    )
    for case in cases:
        snapshot, context = load_toy_snapshot(ROOT / f"cases/toy/{case}.yaml")
        runtime = build_field_runtime(snapshot, context)
        prepared = build_progression_lookup(snapshot, context)
        xy_points = _cell_midpoints(prepared.x_coords, prepared.y_coords)
        exact = runtime.query_progression_points(xy_points[:, 0], xy_points[:, 1])["progression_tilted"]
        lookup = query_progression_lookup_points(prepared, xy_points)
        diff = np.abs(exact - lookup)

        assert float(np.max(diff)) < 0.16
        assert float(np.mean(diff)) < 0.03


def test_progression_lookup_preserves_top_k_trajectory_ordering_for_representative_cases() -> None:
    clear_progression_lookup_cache()
    for case in ("left_bend", "u_turn"):
        snapshot, context = load_toy_snapshot(ROOT / f"cases/toy/{case}.yaml")
        runtime = build_field_runtime(snapshot, context)
        prepared = build_progression_lookup(snapshot, context)
        guide_points = snapshot.progression_support.guides[0].points
        trajectories_xy = _offset_trajectory_family(guide_points, steps=16)

        exact_scores = np.sum(runtime.query_progression_trajectories(trajectories_xy)["progression_tilted"], axis=1)
        lookup_scores = np.sum(query_progression_lookup_trajectories(prepared, trajectories_xy), axis=1)
        exact_top = np.argsort(exact_scores)[-3:]
        lookup_top = np.argsort(lookup_scores)[-3:]

        assert int(np.argmax(lookup_scores)) == int(np.argmax(exact_scores))
        assert set(lookup_top.tolist()) == set(exact_top.tolist())


def test_raster_sampling_exposes_lookup_visualization_channels() -> None:
    clear_progression_lookup_cache()
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")
    raster = sample_local_raster(snapshot, context, x_samples=48, y_samples=48)

    assert "planner_lookup_progression_tilted" in raster.channels
    assert "planner_lookup_error" in raster.channels
    assert raster.channels["planner_lookup_progression_tilted"].shape == raster.channels["progression_tilted"].shape
    assert raster.channels["planner_lookup_error"].shape == raster.channels["progression_tilted"].shape
    assert "planner_lookup" in raster.metadata
    assert raster.metadata["planner_lookup"]["cache_policy"] == "cold_build"
    assert set(raster.metadata["planner_lookup"]["timing_s"]) == {
        "exact_query_grid",
        "lookup_cold_build",
        "lookup_query_grid",
    }


def _cell_midpoints(x_coords: np.ndarray, y_coords: np.ndarray) -> np.ndarray:
    x_mid = (x_coords[:-1] + x_coords[1:]) * 0.5 if x_coords.size > 1 else x_coords
    y_mid = (y_coords[:-1] + y_coords[1:]) * 0.5 if y_coords.size > 1 else y_coords
    x_step = max(1, int(np.ceil(x_mid.size / 6)))
    y_step = max(1, int(np.ceil(y_mid.size / 6)))
    sample_x = x_mid[::x_step]
    sample_y = y_mid[::y_step]
    grid_x, grid_y = np.meshgrid(sample_x, sample_y)
    return np.column_stack([grid_x.ravel(), grid_y.ravel()])


def _offset_trajectory_family(points: tuple[Point2, ...], *, steps: int) -> np.ndarray:
    centerline = _resample_polyline(points, steps)
    tangents = np.zeros_like(centerline)
    tangents[1:-1] = centerline[2:] - centerline[:-2]
    tangents[0] = centerline[1] - centerline[0]
    tangents[-1] = centerline[-1] - centerline[-2]
    norms = np.linalg.norm(tangents, axis=1, keepdims=True)
    tangents = np.divide(tangents, norms, out=np.zeros_like(tangents), where=norms > 1e-9)
    normals = np.column_stack([-tangents[:, 1], tangents[:, 0]])
    offsets = np.asarray([-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8], dtype=float)
    trajectories = [centerline + offset * normals for offset in offsets]
    return np.asarray(trajectories, dtype=float)


def _resample_polyline(points: tuple[Point2, ...], steps: int) -> np.ndarray:
    if len(points) == 0:
        return np.zeros((steps, 2), dtype=float)
    if len(points) == 1:
        return np.repeat(np.asarray([points[0]], dtype=float), steps, axis=0)
    point_array = np.asarray(points, dtype=float)
    segment_lengths = np.linalg.norm(point_array[1:] - point_array[:-1], axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(segment_lengths)])
    total_length = float(cumulative[-1])
    if total_length <= 1e-9:
        return np.repeat(point_array[:1], steps, axis=0)
    targets = np.linspace(0.0, total_length, steps)
    result = np.zeros((steps, 2), dtype=float)
    segment_index = 0
    for index, target in enumerate(targets):
        while segment_index < len(segment_lengths) - 1 and cumulative[segment_index + 1] < target:
            segment_index += 1
        start = point_array[segment_index]
        end = point_array[segment_index + 1]
        start_s = cumulative[segment_index]
        stop_s = cumulative[segment_index + 1]
        ratio = 0.0 if stop_s - start_s <= 1e-9 else (target - start_s) / (stop_s - start_s)
        result[index] = start + ratio * (end - start)
    return result
