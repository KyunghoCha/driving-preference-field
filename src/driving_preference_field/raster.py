from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .channels import continuity_branch, interior_boundary
from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample
from .exception_layers import evaluate_exception_layers
from .progression_surface import progression_surface_grid


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
    channels = {
        "progression_tilted": np.zeros(shape, dtype=float),
        "interior_boundary": np.zeros(shape, dtype=float),
        "continuity_branch": np.zeros(shape, dtype=float),
        "base_preference_total": np.zeros(shape, dtype=float),
        "safety_soft": np.zeros(shape, dtype=float),
        "rule_soft": np.zeros(shape, dtype=float),
        "dynamic_soft": np.zeros(shape, dtype=float),
        "hard_unsafe_mask": np.zeros(shape, dtype=bool),
        "hard_rule_mask": np.zeros(shape, dtype=bool),
        "hard_dynamic_mask": np.zeros(shape, dtype=bool),
    }

    progression_grid = progression_surface_grid(
        snapshot,
        context,
        config=field_config.progression,
        x_coords=x_coords,
        y_coords=y_coords,
    )
    channels["progression_tilted"][:, :] = progression_grid

    for yi, y in enumerate(y_coords):
        for xi, x in enumerate(x_coords):
            state = StateSample(x=float(x), y=float(y), yaw=context.ego_pose.yaw)
            interior_value = interior_boundary(snapshot, context, state, config=field_config)
            continuity_value = continuity_branch(snapshot, context, state, config=field_config)
            soft_channels, hard_flags = evaluate_exception_layers(snapshot, context, state)
            channels["interior_boundary"][yi, xi] = interior_value
            channels["continuity_branch"][yi, xi] = continuity_value
            channels["base_preference_total"][yi, xi] = (
                progression_grid[yi, xi] + interior_value + continuity_value
            )
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
        },
    )
