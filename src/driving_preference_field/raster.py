from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample
from .exception_layers import evaluate_exception_layers
from .field_runtime import build_field_runtime
from .planner_lookup import build_progression_lookup, query_progression_lookup_trajectories


@dataclass(frozen=True)
class RasterSampleResult:
    x_coords: np.ndarray
    y_coords: np.ndarray
    channels: dict[str, np.ndarray]
    metadata: dict[str, object]


def _cell_centers(start: float, stop: float, samples: int) -> np.ndarray:
    if samples <= 0:
        raise ValueError("samples must be positive")
    step = (stop - start) / samples
    return np.linspace(start, stop, samples, endpoint=False, dtype=float) + step * 0.5


def sample_local_raster(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig | None = None,
    x_samples: int = 160,
    y_samples: int = 160,
) -> RasterSampleResult:
    field_config = config or DEFAULT_FIELD_CONFIG
    x_coords = _cell_centers(context.local_window.x_min, context.local_window.x_max, x_samples)
    y_coords = _cell_centers(context.local_window.y_min, context.local_window.y_max, y_samples)
    shape = (y_samples, x_samples)

    runtime = build_field_runtime(snapshot, context, config=field_config)
    exact_start = time.perf_counter()
    channels = runtime.query_debug_grid(x_coords, y_coords)
    exact_query_s = time.perf_counter() - exact_start
    grid_x, grid_y = np.meshgrid(x_coords, y_coords)
    lookup_build_start = time.perf_counter()
    lookup = build_progression_lookup(snapshot, context, config=field_config)
    lookup_build_s = time.perf_counter() - lookup_build_start
    lookup_query_start = time.perf_counter()
    lookup_scores = query_progression_lookup_trajectories(
        lookup,
        np.stack([grid_x, grid_y], axis=-1).reshape(1, -1, 2),
    ).reshape(shape)
    lookup_query_s = time.perf_counter() - lookup_query_start
    channels["planner_lookup_progression_tilted"] = lookup_scores
    channels["planner_lookup_error"] = lookup_scores - channels["progression_tilted"]

    channels.update(
        {
            "safety_soft": np.zeros(shape, dtype=float),
            "rule_soft": np.zeros(shape, dtype=float),
            "dynamic_soft": np.zeros(shape, dtype=float),
            "hard_unsafe_mask": np.zeros(shape, dtype=bool),
            "hard_rule_mask": np.zeros(shape, dtype=bool),
            "hard_dynamic_mask": np.zeros(shape, dtype=bool),
        }
    )
    for yi, y in enumerate(y_coords):
        for xi, x in enumerate(x_coords):
            state = StateSample(x=float(x), y=float(y), yaw=context.ego_pose.yaw)
            soft_channels, hard_flags = evaluate_exception_layers(snapshot, context, state)
            channels["safety_soft"][yi, xi] = soft_channels["safety_soft"]
            channels["rule_soft"][yi, xi] = soft_channels["rule_soft"]
            channels["dynamic_soft"][yi, xi] = soft_channels["dynamic_soft"]
            channels["hard_unsafe_mask"][yi, xi] = hard_flags["unsafe"]
            channels["hard_rule_mask"][yi, xi] = hard_flags["rule_blocked"]
            channels["hard_dynamic_mask"][yi, xi] = hard_flags["dynamic_blocked"]

    return RasterSampleResult(
        x_coords=x_coords,
        y_coords=y_coords,
        channels=channels,
        metadata={
            "x_samples": x_samples,
            "y_samples": y_samples,
            "query_window": {
                "x_min": context.local_window.x_min,
                "x_max": context.local_window.x_max,
                "y_min": context.local_window.y_min,
                "y_max": context.local_window.y_max,
            },
            "field_config": field_config.to_dict(),
            "planner_lookup": {
                "cache_key": lookup.cache_key,
                **lookup.build_metadata,
                "timing_s": {
                    "exact_query_grid": exact_query_s,
                    "lookup_build": lookup_build_s,
                    "lookup_query_grid": lookup_query_s,
                },
            },
        },
    )
