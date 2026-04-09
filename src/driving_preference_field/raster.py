from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot
from .field_runtime import build_field_runtime


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
        "progression_s_hat": np.zeros(shape, dtype=float),
        "progression_n_hat": np.zeros(shape, dtype=float),
        "progression_longitudinal_component": np.zeros(shape, dtype=float),
        "progression_transverse_component": np.zeros(shape, dtype=float),
        "progression_support_mod": np.zeros(shape, dtype=float),
        "progression_alignment_mod": np.zeros(shape, dtype=float),
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

    runtime = build_field_runtime(snapshot, context, config=field_config)
    channels.update(runtime.query_debug_grid(x_coords, y_coords))

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
