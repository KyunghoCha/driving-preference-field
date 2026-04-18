from __future__ import annotations

"""Internal planner-facing scalar lookup backend.

This module keeps the exact progression runtime as the semantic oracle and
adds a scene-level cached 2D scalar lookup for repeated planner queries. It is
intentionally internal and does not change the public runtime contract.
"""

from collections import OrderedDict
from dataclasses import asdict, dataclass
from hashlib import sha1
import json

import numpy as np

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, QueryWindow, SemanticInputSnapshot
from .field_runtime import build_field_runtime

_DEFAULT_LOOKUP_GRID_SPACING_M = 0.10
_LOOKUP_CACHE_MAXSIZE = 8


@dataclass(frozen=True)
class PreparedProgressionLookup:
    local_window: QueryWindow
    x_coords: np.ndarray
    y_coords: np.ndarray
    progression_tilted: np.ndarray
    cache_key: str
    build_metadata: dict[str, object]


_LOOKUP_CACHE: OrderedDict[str, PreparedProgressionLookup] = OrderedDict()


def clear_progression_lookup_cache() -> None:
    _LOOKUP_CACHE.clear()


def build_progression_lookup(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig | None = None,
    grid_spacing_m: float = _DEFAULT_LOOKUP_GRID_SPACING_M,
) -> PreparedProgressionLookup:
    if grid_spacing_m <= 0.0:
        raise ValueError("grid_spacing_m must be positive")
    field_config = config or DEFAULT_FIELD_CONFIG
    cache_key = _lookup_cache_key(snapshot, context, field_config, grid_spacing_m)
    cached = _LOOKUP_CACHE.get(cache_key)
    if cached is not None:
        _LOOKUP_CACHE.move_to_end(cache_key)
        return cached

    x_coords = _metric_coords(context.local_window.x_min, context.local_window.x_max, grid_spacing_m)
    y_coords = _metric_coords(context.local_window.y_min, context.local_window.y_max, grid_spacing_m)
    runtime = build_field_runtime(snapshot, context, config=field_config)
    progression_tilted = runtime.query_debug_grid(x_coords, y_coords)["progression_tilted"]
    prepared = PreparedProgressionLookup(
        local_window=context.local_window,
        x_coords=x_coords,
        y_coords=y_coords,
        progression_tilted=progression_tilted,
        cache_key=cache_key,
        build_metadata={
            "grid_spacing_m": float(grid_spacing_m),
            "x_count": int(x_coords.size),
            "y_count": int(y_coords.size),
            "field_config": field_config.to_dict(),
            "window": {
                "x_min": context.local_window.x_min,
                "x_max": context.local_window.x_max,
                "y_min": context.local_window.y_min,
                "y_max": context.local_window.y_max,
            },
        },
    )
    _LOOKUP_CACHE[cache_key] = prepared
    _LOOKUP_CACHE.move_to_end(cache_key)
    while len(_LOOKUP_CACHE) > _LOOKUP_CACHE_MAXSIZE:
        _LOOKUP_CACHE.popitem(last=False)
    return prepared


def query_progression_lookup_points(
    prepared: PreparedProgressionLookup,
    xy_points: np.ndarray,
) -> np.ndarray:
    xy_points = np.asarray(xy_points, dtype=float)
    if xy_points.ndim != 2 or xy_points.shape[1] != 2:
        raise ValueError("xy_points must have shape (count, 2)")
    if xy_points.shape[0] == 0:
        return np.zeros((0,), dtype=float)
    return _bilinear_lookup(
        prepared.progression_tilted,
        prepared.x_coords,
        prepared.y_coords,
        xy_points[:, 0],
        xy_points[:, 1],
    )


def query_progression_lookup_trajectories(
    prepared: PreparedProgressionLookup,
    trajectories_xy: np.ndarray,
) -> np.ndarray:
    trajectories_xy = np.asarray(trajectories_xy, dtype=float)
    if trajectories_xy.ndim != 3 or trajectories_xy.shape[-1] != 2:
        raise ValueError("trajectories_xy must have shape (batch, steps, 2)")
    batch_shape = trajectories_xy.shape[:-1]
    flat_xy = trajectories_xy.reshape(-1, 2)
    return query_progression_lookup_points(prepared, flat_xy).reshape(batch_shape)


def _metric_coords(start: float, stop: float, spacing: float) -> np.ndarray:
    if stop < start:
        raise ValueError("lookup window bounds must satisfy stop >= start")
    if abs(stop - start) <= 1e-9:
        return np.asarray([start], dtype=float)
    count = int(np.floor((stop - start) / spacing)) + 1
    coords = start + spacing * np.arange(count, dtype=float)
    if coords[-1] < stop - 1e-9:
        coords = np.append(coords, float(stop))
    else:
        coords[-1] = float(stop)
    return coords


def _bilinear_lookup(
    grid: np.ndarray,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    x_values: np.ndarray,
    y_values: np.ndarray,
) -> np.ndarray:
    x_values = np.clip(np.asarray(x_values, dtype=float), x_coords[0], x_coords[-1])
    y_values = np.clip(np.asarray(y_values, dtype=float), y_coords[0], y_coords[-1])
    if x_coords.size == 1 and y_coords.size == 1:
        return np.full(x_values.shape, float(grid[0, 0]), dtype=float)
    if x_coords.size == 1:
        return _linear_interp_axis(grid[:, 0], y_coords, y_values)
    if y_coords.size == 1:
        return _linear_interp_axis(grid[0, :], x_coords, x_values)

    x_index = np.searchsorted(x_coords, x_values, side="right") - 1
    y_index = np.searchsorted(y_coords, y_values, side="right") - 1
    x_index = np.clip(x_index, 0, x_coords.size - 2)
    y_index = np.clip(y_index, 0, y_coords.size - 2)

    x0 = x_coords[x_index]
    x1 = x_coords[x_index + 1]
    y0 = y_coords[y_index]
    y1 = y_coords[y_index + 1]
    tx = np.divide(
        x_values - x0,
        x1 - x0,
        out=np.zeros_like(x_values),
        where=np.abs(x1 - x0) > 1e-12,
    )
    ty = np.divide(
        y_values - y0,
        y1 - y0,
        out=np.zeros_like(y_values),
        where=np.abs(y1 - y0) > 1e-12,
    )

    v00 = grid[y_index, x_index]
    v10 = grid[y_index, x_index + 1]
    v01 = grid[y_index + 1, x_index]
    v11 = grid[y_index + 1, x_index + 1]
    return (
        (1.0 - tx) * (1.0 - ty) * v00
        + tx * (1.0 - ty) * v10
        + (1.0 - tx) * ty * v01
        + tx * ty * v11
    )


def _linear_interp_axis(values: np.ndarray, coords: np.ndarray, query: np.ndarray) -> np.ndarray:
    index = np.searchsorted(coords, query, side="right") - 1
    index = np.clip(index, 0, coords.size - 2)
    c0 = coords[index]
    c1 = coords[index + 1]
    t = np.divide(
        query - c0,
        c1 - c0,
        out=np.zeros_like(query),
        where=np.abs(c1 - c0) > 1e-12,
    )
    v0 = values[index]
    v1 = values[index + 1]
    return (1.0 - t) * v0 + t * v1


def _lookup_cache_key(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    config: FieldConfig,
    grid_spacing_m: float,
) -> str:
    payload = {
        "semantic_snapshot": asdict(snapshot),
        "ego_pose": asdict(context.ego_pose),
        "local_window": asdict(context.local_window),
        "mode": context.mode,
        "phase": context.phase,
        "field_config": config.to_dict(),
        "grid_spacing_m": round(float(grid_spacing_m), 6),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=repr)
    return sha1(encoded.encode("utf-8")).hexdigest()
