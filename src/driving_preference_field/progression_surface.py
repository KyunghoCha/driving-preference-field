from __future__ import annotations

"""Current progression surface implementation.

This module treats progression and branch guides as control structure for a
continuous local-space coordinate field. The runtime first estimates blended
coordinates over the local map and then evaluates an additive whole-fabric
score:

    progression_tilted(p)
      = support_mod * alignment_mod * (T(n_hat) + gain * L(u))

The exact formula here is a current implementation detail, not canonical truth.
README and docs/reading/current_implementation_formula_reference_ko.md must move
with this module when the implementation changes.
"""

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from .config import ProgressionConfig
from .contracts import Point2, QueryContext, SemanticInputSnapshot, StateSample
from .geometry import clamp, polyline_length

_ANCHOR_SPACING_M = 0.20
_SPLINE_SAMPLE_DENSITY_M = 0.05
_SPLINE_MIN_SUBDIVISIONS = 8
_MIN_SIGMA_T = 0.40
_MIN_SIGMA_N = 0.35
_SIGMA_T_SCALE = 0.35
_SIGMA_N_SCALE = 1.50
_END_EXTENSION_M = 2.0
_QUERY_BATCH_SIZE = 4096
_SUPPORT_BASE = 0.95
_SUPPORT_RANGE = 0.05
_ALIGNMENT_BASE = 0.95
_ALIGNMENT_RANGE = 0.05
_DOMINANT_GUIDE_WEIGHT_EPS = 1e-4
_EFFECTIVE_ANCHOR_WEIGHT_EPS = 1e-3
_EPS = 1e-9


@dataclass(frozen=True)
class SurfaceGuide:
    guide_id: str
    points: tuple[Point2, ...]
    guide_length: float
    weight: float
    confidence: float


@dataclass(frozen=True)
class SurfaceIndex:
    signature: tuple[tuple[object, ...], ...]
    guides: tuple[SurfaceGuide, ...]
    guide_points: tuple[tuple[str, tuple[Point2, ...]], ...]
    guide_ids: tuple[str, ...]
    max_guide_length: float
    min_progress_extent: float
    max_progress_extent: float
    anchor_points: np.ndarray
    anchor_tangents: np.ndarray
    anchor_normals: np.ndarray
    anchor_cumulative_s: np.ndarray
    anchor_guide_lengths: np.ndarray
    anchor_guide_weights: np.ndarray
    anchor_confidences: np.ndarray
    anchor_guide_indices: np.ndarray


@dataclass(frozen=True)
class BlendResult:
    anchor_indices: np.ndarray
    raw_weights: np.ndarray
    blend_weights: np.ndarray
    s_hat: np.ndarray
    n_hat: np.ndarray
    tangent_hat: np.ndarray
    support_sum: np.ndarray
    anchor_count: int


class ProgressionSurfaceRuntime:
    """Cached runtime view over the current progression field implementation."""

    def __init__(
        self,
        snapshot: SemanticInputSnapshot,
        context: QueryContext,
        *,
        config: ProgressionConfig,
    ) -> None:
        self._snapshot = snapshot
        self._context = context
        self._config = config
        self._surface = _surface_index(snapshot)
        self._ego_s_hat = (
            _ego_s_hat(self._surface, context, config)
            if config.longitudinal_frame == "ego_relative"
            else None
        )

    @property
    def surface(self) -> SurfaceIndex:
        return self._surface

    @property
    def config(self) -> ProgressionConfig:
        return self._config

    def query_state(self, state: StateSample) -> dict[str, object]:
        if self._config.support_ceiling <= 0.0 or self._surface.anchor_points.size == 0:
            return {
                "score": 0.0,
                "anchor_count": 0,
                "support_sum": 0.0,
                "support_mod": 0.0,
                "alignment_mod": 0.0,
                "longitudinal_component": 0.0,
                "transverse_component": 0.0,
                "s_hat": 0.0,
                "n_hat": 0.0,
                "blended_progress": 0.0,
                "dominant_guides": (),
                "longitudinal_frame": self._config.longitudinal_frame,
            }
        arrays = self._query_arrays(
            np.asarray([state.x], dtype=float),
            np.asarray([state.y], dtype=float),
            np.asarray([state.yaw], dtype=float),
            include_internal=True,
        )
        dominant_guides = _dominant_guides(
            self._surface,
            arrays["_anchor_indices"][:, 0],
            arrays["_blend_weights"][:, 0],
        )
        return {
            "score": float(arrays["score"][0]),
            "anchor_count": int(arrays["effective_anchor_count"][0]),
            "support_sum": float(arrays["support_sum"][0]),
            "support_mod": float(arrays["support_mod"][0]),
            "alignment_mod": float(arrays["alignment_mod"][0]),
            "longitudinal_component": float(arrays["longitudinal_component"][0]),
            "transverse_component": float(arrays["transverse_component"][0]),
            "s_hat": float(arrays["s_hat"][0]),
            "n_hat": float(arrays["n_hat"][0]),
            "blended_progress": float(arrays["s_hat"][0]),
            "dominant_guides": dominant_guides,
            "longitudinal_frame": self._config.longitudinal_frame,
        }

    def query_grid(self, x_coords: np.ndarray, y_coords: np.ndarray) -> dict[str, np.ndarray]:
        if x_coords.ndim != 1 or y_coords.ndim != 1:
            raise ValueError("x_coords and y_coords must be 1-D arrays")
        if self._surface.anchor_points.size == 0 or self._config.support_ceiling <= 0.0:
            shape = (len(y_coords), len(x_coords))
            return {
                "score": np.zeros(shape, dtype=float),
                "s_hat": np.zeros(shape, dtype=float),
                "n_hat": np.zeros(shape, dtype=float),
                "support_sum": np.zeros(shape, dtype=float),
                "support_mod": np.zeros(shape, dtype=float),
                "alignment_mod": np.zeros(shape, dtype=float),
                "longitudinal_component": np.zeros(shape, dtype=float),
                "transverse_component": np.zeros(shape, dtype=float),
            }

        grid_x, grid_y = np.meshgrid(x_coords, y_coords)
        flat_yaw = np.full(grid_x.size, self._context.ego_pose.yaw, dtype=float)
        arrays = self._query_arrays(
            grid_x.ravel(),
            grid_y.ravel(),
            flat_yaw,
            include_internal=False,
        )
        shape = (len(y_coords), len(x_coords))
        return {
            "score": arrays["score"].reshape(shape),
            "s_hat": arrays["s_hat"].reshape(shape),
            "n_hat": arrays["n_hat"].reshape(shape),
            "support_sum": arrays["support_sum"].reshape(shape),
            "support_mod": arrays["support_mod"].reshape(shape),
            "alignment_mod": arrays["alignment_mod"].reshape(shape),
            "longitudinal_component": arrays["longitudinal_component"].reshape(shape),
            "transverse_component": arrays["transverse_component"].reshape(shape),
        }

    def query_points(
        self,
        x_values: np.ndarray,
        y_values: np.ndarray,
        heading_yaws: np.ndarray | None = None,
    ) -> dict[str, np.ndarray]:
        x_values = np.asarray(x_values, dtype=float)
        y_values = np.asarray(y_values, dtype=float)
        if x_values.ndim != 1 or y_values.ndim != 1:
            raise ValueError("x_values and y_values must be 1-D arrays")
        if x_values.shape != y_values.shape:
            raise ValueError("x_values and y_values must have the same shape")
        if heading_yaws is None:
            heading_yaws = np.full(x_values.shape, self._context.ego_pose.yaw, dtype=float)
        else:
            heading_yaws = np.asarray(heading_yaws, dtype=float)
            if heading_yaws.ndim != 1 or heading_yaws.shape != x_values.shape:
                raise ValueError("heading_yaws must be a 1-D array with the same shape as x_values")
        arrays = self._query_arrays(x_values, y_values, heading_yaws, include_internal=False)
        return {
            "progression_tilted": arrays["score"],
            "progression_s_hat": arrays["s_hat"],
            "progression_n_hat": arrays["n_hat"],
            "progression_support_sum": arrays["support_sum"],
            "progression_support_mod": arrays["support_mod"],
            "progression_alignment_mod": arrays["alignment_mod"],
            "progression_longitudinal_component": arrays["longitudinal_component"],
            "progression_transverse_component": arrays["transverse_component"],
        }

    def query_trajectories(
        self,
        trajectories_xy: np.ndarray,
        heading_yaws: np.ndarray | None = None,
    ) -> dict[str, np.ndarray]:
        trajectories_xy = np.asarray(trajectories_xy, dtype=float)
        if trajectories_xy.ndim != 3 or trajectories_xy.shape[-1] != 2:
            raise ValueError("trajectories_xy must have shape (batch, steps, 2)")
        batch_shape = trajectories_xy.shape[:-1]
        flat_xy = trajectories_xy.reshape(-1, 2)
        if heading_yaws is None:
            flat_yaws = np.full((flat_xy.shape[0],), self._context.ego_pose.yaw, dtype=float)
        else:
            heading_yaws = np.asarray(heading_yaws, dtype=float)
            if heading_yaws.shape != batch_shape:
                raise ValueError("heading_yaws must have shape trajectories_xy.shape[:-1]")
            flat_yaws = heading_yaws.reshape(-1)
        flat_result = self.query_points(flat_xy[:, 0], flat_xy[:, 1], flat_yaws)
        return {name: values.reshape(batch_shape) for name, values in flat_result.items()}

    def _query_arrays(
        self,
        x_values: np.ndarray,
        y_values: np.ndarray,
        heading_yaws: np.ndarray,
        *,
        include_internal: bool,
    ) -> dict[str, np.ndarray]:
        point_count = x_values.size
        if point_count == 0 or self._config.support_ceiling <= 0.0 or self._surface.anchor_points.size == 0:
            empty = np.zeros((0,), dtype=float)
            return {
                "score": empty,
                "s_hat": empty,
                "n_hat": empty,
                "support_sum": empty,
                "support_mod": empty,
                "alignment_mod": empty,
                "longitudinal_component": empty,
                "transverse_component": empty,
                "effective_anchor_count": empty.astype(int),
            }

        chunks: dict[str, list[np.ndarray]] = {
            "score": [],
            "s_hat": [],
            "n_hat": [],
            "support_sum": [],
            "support_mod": [],
            "alignment_mod": [],
            "longitudinal_component": [],
            "transverse_component": [],
            "effective_anchor_count": [],
        }
        internal_chunks: dict[str, list[np.ndarray]] = {"_anchor_indices": [], "_blend_weights": []}

        for start in range(0, point_count, _QUERY_BATCH_SIZE):
            stop = min(point_count, start + _QUERY_BATCH_SIZE)
            blend = _blend_coordinates(
                self._surface,
                x_values[start:stop],
                y_values[start:stop],
                self._config,
            )
            longitudinal_component, transverse_component, support_mod, alignment_mod = _surface_components(
                self._surface,
                blend,
                config=self._config,
                heading_yaws=heading_yaws[start:stop],
                ego_s_hat=self._ego_s_hat,
            )
            score = support_mod * alignment_mod * (
                transverse_component + self._config.longitudinal_gain * longitudinal_component
            )
            effective_anchor_count = np.sum(
                blend.blend_weights > _EFFECTIVE_ANCHOR_WEIGHT_EPS,
                axis=0,
                dtype=int,
            )
            chunks["score"].append(score)
            chunks["s_hat"].append(blend.s_hat)
            chunks["n_hat"].append(blend.n_hat)
            chunks["support_sum"].append(blend.support_sum)
            chunks["support_mod"].append(support_mod)
            chunks["alignment_mod"].append(alignment_mod)
            chunks["longitudinal_component"].append(longitudinal_component)
            chunks["transverse_component"].append(transverse_component)
            chunks["effective_anchor_count"].append(effective_anchor_count)
            if include_internal:
                internal_chunks["_anchor_indices"].append(blend.anchor_indices)
                internal_chunks["_blend_weights"].append(blend.blend_weights)

        result = {name: np.concatenate(parts) for name, parts in chunks.items()}
        if include_internal:
            result["_anchor_indices"] = np.concatenate(internal_chunks["_anchor_indices"], axis=1)
            result["_blend_weights"] = np.concatenate(internal_chunks["_blend_weights"], axis=1)
        return result


def build_progression_surface_runtime(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: ProgressionConfig,
) -> ProgressionSurfaceRuntime:
    return ProgressionSurfaceRuntime(snapshot, context, config=config)


def progression_surface_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: ProgressionConfig,
) -> dict[str, object]:
    if config.support_ceiling <= 0.0:
        return {
            "score": 0.0,
            "anchor_count": 0,
            "support_sum": 0.0,
            "support_mod": 0.0,
            "alignment_mod": 0.0,
            "longitudinal_component": 0.0,
            "transverse_component": 0.0,
            "s_hat": 0.0,
            "n_hat": 0.0,
            "blended_progress": 0.0,
            "dominant_guides": (),
            "longitudinal_frame": config.longitudinal_frame,
        }
    runtime = build_progression_surface_runtime(snapshot, context, config=config)
    return runtime.query_state(state)


def progression_surface_grid(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: ProgressionConfig,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
) -> np.ndarray:
    runtime = build_progression_surface_runtime(snapshot, context, config=config)
    return runtime.query_grid(x_coords, y_coords)["score"]


def progression_surface_grid_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: ProgressionConfig,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
) -> dict[str, np.ndarray]:
    runtime = build_progression_surface_runtime(snapshot, context, config=config)
    return runtime.query_grid(x_coords, y_coords)


def _surface_components(
    surface: SurfaceIndex,
    blend: BlendResult,
    *,
    config: ProgressionConfig,
    heading_yaws: np.ndarray,
    ego_s_hat: float | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if blend.anchor_count == 0:
        zeros = np.zeros_like(blend.s_hat)
        return zeros, zeros, zeros, zeros

    progress_span = max(surface.max_progress_extent - surface.min_progress_extent, _EPS)
    if config.longitudinal_frame == "local_absolute":
        u_value = np.clip((blend.s_hat - surface.min_progress_extent) / progress_span, 0.0, 1.0)
    else:
        lookahead = max(_ego_relative_lookahead(surface, config), _EPS)
        reference_s = float(ego_s_hat or 0.0)
        u_value = np.clip(np.maximum(0.0, blend.s_hat - reference_s) / lookahead, 0.0, 1.0)

    transverse_ratio = blend.n_hat / max(config.transverse_scale, _EPS)
    transverse_component = _transverse_value_array(transverse_ratio, config)
    longitudinal_component = _longitudinal_value_array(u_value, config)

    heading_x = np.cos(heading_yaws)
    heading_y = np.sin(heading_yaws)
    alignment_quality = np.maximum(
        0.0,
        heading_x * blend.tangent_hat[:, 0] + heading_y * blend.tangent_hat[:, 1],
    )
    alignment_mod = _ALIGNMENT_BASE + _ALIGNMENT_RANGE * alignment_quality

    clipped_confidence = np.minimum(
        surface.anchor_confidences[:, None],
        max(config.support_ceiling, _EPS),
    )
    support_quality = np.sum(blend.blend_weights * clipped_confidence, axis=0) / max(
        config.support_ceiling,
        _EPS,
    )
    support_mod = _SUPPORT_BASE + _SUPPORT_RANGE * np.clip(support_quality, 0.0, 1.0)
    return longitudinal_component, transverse_component, support_mod, alignment_mod


def _blend_coordinates(
    surface: SurfaceIndex,
    x_values: np.ndarray,
    y_values: np.ndarray,
    config: ProgressionConfig,
) -> BlendResult:
    if surface.anchor_points.size == 0:
        empty = np.zeros((0, x_values.size), dtype=float)
        tangent_hat = np.zeros((x_values.size, 2), dtype=float)
        return BlendResult(
            anchor_indices=np.zeros((0, x_values.size), dtype=int),
            raw_weights=empty,
            blend_weights=empty,
            s_hat=np.zeros_like(x_values),
            n_hat=np.zeros_like(x_values),
            tangent_hat=tangent_hat,
            support_sum=np.zeros_like(x_values),
            anchor_count=0,
        )

    anchor_count = surface.anchor_points.shape[0]
    anchor_indices = np.repeat(np.arange(anchor_count, dtype=int)[:, None], x_values.size, axis=1)
    points_x = surface.anchor_points[:, 0][:, None]
    points_y = surface.anchor_points[:, 1][:, None]
    dx = x_values[None, :] - points_x
    dy = y_values[None, :] - points_y

    tangent_x = surface.anchor_tangents[:, 0][:, None]
    tangent_y = surface.anchor_tangents[:, 1][:, None]
    normal_x = surface.anchor_normals[:, 0][:, None]
    normal_y = surface.anchor_normals[:, 1][:, None]
    cumulative_s = surface.anchor_cumulative_s[:, None]
    guide_lengths = surface.anchor_guide_lengths[:, None]
    guide_weights = surface.anchor_guide_weights[:, None]
    confidences = surface.anchor_confidences[:, None]

    tau = dx * tangent_x + dy * tangent_y
    nu = dx * normal_x + dy * normal_y

    sigma_t = np.maximum(_MIN_SIGMA_T, guide_lengths * config.lookahead_scale * _SIGMA_T_SCALE)
    sigma_n = max(_MIN_SIGMA_N, config.transverse_scale * _SIGMA_N_SCALE)
    raw_weights = guide_weights * confidences * np.exp(
        -0.5 * (((tau / sigma_t) ** 2) + ((nu / sigma_n) ** 2))
    )
    support_sum = np.sum(raw_weights, axis=0)
    blend_weights = raw_weights / np.clip(support_sum, _EPS, None)

    s_values = cumulative_s + tau
    s_hat = np.sum(blend_weights * s_values, axis=0)
    n_hat = np.sqrt(np.sum(blend_weights * (nu**2), axis=0))
    tangent_hat = np.stack(
        (
            np.sum(blend_weights * tangent_x, axis=0),
            np.sum(blend_weights * tangent_y, axis=0),
        ),
        axis=1,
    )
    tangent_norm = np.linalg.norm(tangent_hat, axis=1, keepdims=True)
    tangent_hat = tangent_hat / np.clip(tangent_norm, _EPS, None)
    return BlendResult(
        anchor_indices=anchor_indices,
        raw_weights=raw_weights,
        blend_weights=blend_weights,
        s_hat=s_hat,
        n_hat=n_hat,
        tangent_hat=tangent_hat,
        support_sum=support_sum,
        anchor_count=anchor_count,
    )


def _dominant_guides(
    surface: SurfaceIndex,
    anchor_indices: np.ndarray,
    blend_weights: np.ndarray,
) -> tuple[tuple[str, float], ...]:
    per_guide: dict[str, float] = {}
    for anchor_index, weight in zip(anchor_indices.tolist(), blend_weights.tolist(), strict=False):
        if weight <= _DOMINANT_GUIDE_WEIGHT_EPS:
            continue
        guide_id = surface.guide_ids[int(surface.anchor_guide_indices[int(anchor_index)])]
        per_guide[guide_id] = per_guide.get(guide_id, 0.0) + float(weight)
    ranked = sorted(per_guide.items(), key=lambda item: item[1], reverse=True)
    return tuple(ranked[:3])


def _ego_s_hat(
    surface: SurfaceIndex,
    context: QueryContext,
    config: ProgressionConfig,
) -> float:
    return _ego_s_hat_cached(
        surface.signature,
        round(context.ego_pose.x, 6),
        round(context.ego_pose.y, 6),
        round(config.lookahead_scale, 6),
        round(config.transverse_scale, 6),
    )


@lru_cache(maxsize=128)
def _ego_s_hat_cached(
    signature: tuple[tuple[object, ...], ...],
    ego_x: float,
    ego_y: float,
    lookahead_scale: float,
    transverse_scale: float,
) -> float:
    surface = _surface_index_from_signature(signature)
    if surface.anchor_points.size == 0:
        return 0.0
    config = ProgressionConfig(
        lookahead_scale=lookahead_scale,
        transverse_scale=transverse_scale,
    )
    blend = _blend_coordinates(
        surface,
        np.asarray([ego_x], dtype=float),
        np.asarray([ego_y], dtype=float),
        config,
    )
    return float(blend.s_hat[0])


def _ego_relative_lookahead(surface: SurfaceIndex, config: ProgressionConfig) -> float:
    return max(_MIN_SIGMA_T, (surface.max_progress_extent - surface.min_progress_extent) * config.lookahead_scale)


def _longitudinal_value_array(u_value: np.ndarray, config: ProgressionConfig) -> np.ndarray:
    u = np.clip(u_value, 0.0, 1.0)
    family = config.longitudinal_family
    shape = max(config.longitudinal_shape, _EPS)
    if family == "linear":
        return u
    if family == "inverse":
        return ((1.0 + shape) * u) / (1.0 + shape * u)
    if family == "power":
        return u**shape
    return np.tanh(shape * u) / max(math.tanh(shape), _EPS)


def _transverse_value_array(ratio: np.ndarray, config: ProgressionConfig) -> np.ndarray:
    family = config.transverse_family
    shape = max(config.transverse_shape, _EPS)
    if family == "inverse":
        return 1.0 / (1.0 + shape * ratio)
    if family == "power":
        return 1.0 / (1.0 + ratio**shape)
    return np.exp(-shape * ratio)


def _surface_index(snapshot: SemanticInputSnapshot) -> SurfaceIndex:
    return _surface_index_from_signature(_surface_signature(snapshot))


def _surface_signature(snapshot: SemanticInputSnapshot) -> tuple[tuple[object, ...], ...]:
    guides = [
        ("progression", guide) for guide in snapshot.progression_support.guides
    ] + [
        ("branch", guide) for guide in snapshot.branch_continuity_support.guides
    ]
    return tuple(
        (
            kind,
            guide.guide_id,
            tuple((round(point[0], 6), round(point[1], 6)) for point in guide.points),
            round(guide.weight, 6),
            round(float(guide.metadata.get("confidence", 1.0)), 6),
        )
        for kind, guide in guides
    )


@lru_cache(maxsize=32)
def _surface_index_from_signature(signature: tuple[tuple[object, ...], ...]) -> SurfaceIndex:
    guides: list[SurfaceGuide] = []
    guide_ids: list[str] = []
    guide_points: list[tuple[str, tuple[Point2, ...]]] = []

    anchor_points: list[Point2] = []
    anchor_tangents: list[Point2] = []
    anchor_normals: list[Point2] = []
    anchor_cumulative_s: list[float] = []
    anchor_guide_lengths: list[float] = []
    anchor_guide_weights: list[float] = []
    anchor_confidences: list[float] = []
    anchor_guide_indices: list[int] = []

    for _, guide_id, points_payload, weight, confidence in signature:
        points = tuple((float(x), float(y)) for x, y in points_payload)
        smooth_points = _smooth_resampled_points(points)
        guide_length = polyline_length(smooth_points)
        if guide_length <= _EPS:
            continue
        guide = SurfaceGuide(
            guide_id=str(guide_id),
            points=smooth_points,
            guide_length=guide_length,
            weight=float(weight),
            confidence=float(confidence),
        )
        guide_index = len(guides)
        guides.append(guide)
        guide_ids.append(guide.guide_id)
        guide_points.append((guide.guide_id, guide.points))
        for cumulative_s, point, tangent in _anchor_points_with_continuation(
            smooth_points,
            extension_length=_END_EXTENSION_M,
        ):
            normal = (-tangent[1], tangent[0])
            anchor_points.append(point)
            anchor_tangents.append(tangent)
            anchor_normals.append(normal)
            anchor_cumulative_s.append(cumulative_s)
            anchor_guide_lengths.append(guide.guide_length)
            anchor_guide_weights.append(guide.weight)
            anchor_confidences.append(guide.confidence)
            anchor_guide_indices.append(guide_index)

    if not anchor_points:
        return SurfaceIndex(
            signature=signature,
            guides=tuple(guides),
            guide_points=tuple(guide_points),
            guide_ids=tuple(guide_ids),
            max_guide_length=0.0,
            min_progress_extent=0.0,
            max_progress_extent=0.0,
            anchor_points=np.zeros((0, 2), dtype=float),
            anchor_tangents=np.zeros((0, 2), dtype=float),
            anchor_normals=np.zeros((0, 2), dtype=float),
            anchor_cumulative_s=np.zeros((0,), dtype=float),
            anchor_guide_lengths=np.zeros((0,), dtype=float),
            anchor_guide_weights=np.zeros((0,), dtype=float),
            anchor_confidences=np.zeros((0,), dtype=float),
            anchor_guide_indices=np.zeros((0,), dtype=int),
        )

    cumulative_array = np.asarray(anchor_cumulative_s, dtype=float)
    return SurfaceIndex(
        signature=signature,
        guides=tuple(guides),
        guide_points=tuple(guide_points),
        guide_ids=tuple(guide_ids),
        max_guide_length=max(anchor_guide_lengths),
        min_progress_extent=float(np.min(cumulative_array)),
        max_progress_extent=float(np.max(cumulative_array)),
        anchor_points=np.asarray(anchor_points, dtype=float),
        anchor_tangents=np.asarray(anchor_tangents, dtype=float),
        anchor_normals=np.asarray(anchor_normals, dtype=float),
        anchor_cumulative_s=cumulative_array,
        anchor_guide_lengths=np.asarray(anchor_guide_lengths, dtype=float),
        anchor_guide_weights=np.asarray(anchor_guide_weights, dtype=float),
        anchor_confidences=np.asarray(anchor_confidences, dtype=float),
        anchor_guide_indices=np.asarray(anchor_guide_indices, dtype=int),
    )


def _smooth_resampled_points(points: tuple[Point2, ...]) -> tuple[Point2, ...]:
    if len(points) < 2:
        return points
    if len(points) == 2:
        return _arc_length_resample(points, spacing=_ANCHOR_SPACING_M)

    dense: list[Point2] = []
    padded = (_reflect_endpoint(points[0], points[1]),) + points + (_reflect_endpoint(points[-1], points[-2]),)
    for index in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[index - 1], padded[index], padded[index + 1], padded[index + 2]
        subdivisions = max(
            _SPLINE_MIN_SUBDIVISIONS,
            int(math.ceil(max(_distance(p1, p2), _EPS) / _SPLINE_SAMPLE_DENSITY_M)),
        )
        for step in range(subdivisions):
            u_value = step / subdivisions
            dense.append(_centripetal_catmull_rom_point(p0, p1, p2, p3, u_value))
    dense.append(points[-1])
    return _arc_length_resample(tuple(dense), spacing=_ANCHOR_SPACING_M)


def _reflect_endpoint(endpoint: Point2, neighbor: Point2) -> Point2:
    return (2.0 * endpoint[0] - neighbor[0], 2.0 * endpoint[1] - neighbor[1])


def _centripetal_catmull_rom_point(
    p0: Point2,
    p1: Point2,
    p2: Point2,
    p3: Point2,
    u_value: float,
) -> Point2:
    alpha = 0.5
    t0 = 0.0
    t1 = t0 + _parameter_step(p0, p1, alpha)
    t2 = t1 + _parameter_step(p1, p2, alpha)
    t3 = t2 + _parameter_step(p2, p3, alpha)
    t = t1 + u_value * (t2 - t1)

    a1 = _lerp_point(p0, p1, _safe_unit_interval(t, t0, t1))
    a2 = _lerp_point(p1, p2, _safe_unit_interval(t, t1, t2))
    a3 = _lerp_point(p2, p3, _safe_unit_interval(t, t2, t3))

    b1 = _lerp_point(a1, a2, _safe_unit_interval(t, t0, t2))
    b2 = _lerp_point(a2, a3, _safe_unit_interval(t, t1, t3))

    return _lerp_point(b1, b2, _safe_unit_interval(t, t1, t2))


def _parameter_step(a: Point2, b: Point2, alpha: float) -> float:
    return max(_distance(a, b) ** alpha, _EPS)


def _safe_unit_interval(value: float, start: float, stop: float) -> float:
    return clamp((value - start) / max(stop - start, _EPS), 0.0, 1.0)


def _lerp_point(a: Point2, b: Point2, t: float) -> Point2:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _distance(a: Point2, b: Point2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _arc_length_resample(points: tuple[Point2, ...], *, spacing: float) -> tuple[Point2, ...]:
    if len(points) < 2:
        return points
    cumulative = [0.0]
    for index in range(1, len(points)):
        cumulative.append(cumulative[-1] + _distance(points[index - 1], points[index]))
    total_length = cumulative[-1]
    if total_length <= _EPS:
        return (points[0], points[-1])

    targets = [0.0]
    distance_cursor = spacing
    while distance_cursor < total_length:
        targets.append(distance_cursor)
        distance_cursor += spacing
    if total_length - targets[-1] > _EPS:
        targets.append(total_length)

    sampled: list[Point2] = []
    segment_index = 0
    for target in targets:
        while segment_index < len(cumulative) - 2 and cumulative[segment_index + 1] < target:
            segment_index += 1
        start_distance = cumulative[segment_index]
        stop_distance = cumulative[segment_index + 1]
        local_t = _safe_unit_interval(target, start_distance, stop_distance)
        sampled.append(_lerp_point(points[segment_index], points[segment_index + 1], local_t))
    return tuple(sampled)


def _anchor_points(points: tuple[Point2, ...]) -> tuple[tuple[float, Point2, Point2], ...]:
    if len(points) < 2:
        return ()
    cumulative = [0.0]
    for index in range(1, len(points)):
        cumulative.append(cumulative[-1] + _distance(points[index - 1], points[index]))

    anchors: list[tuple[float, Point2, Point2]] = []
    for index, point in enumerate(points):
        if index == 0:
            tangent = _segment_tangent(point, points[1])
        elif index == len(points) - 1:
            tangent = _segment_tangent(points[index - 1], point)
        else:
            tangent = _segment_tangent(points[index - 1], points[index + 1])
        anchors.append((cumulative[index], point, tangent))
    return tuple(anchors)


def _anchor_points_with_continuation(
    points: tuple[Point2, ...],
    *,
    extension_length: float,
) -> tuple[tuple[float, Point2, Point2], ...]:
    anchors = list(_anchor_points(points))
    if not anchors:
        return ()
    start_s, start_point, start_tangent = anchors[0]
    end_s, end_point, end_tangent = anchors[-1]

    start_extension: list[tuple[float, Point2, Point2]] = []
    distance_cursor = _ANCHOR_SPACING_M
    while distance_cursor <= extension_length + _EPS:
        start_extension.append(
            (
                start_s - distance_cursor,
                (
                    start_point[0] - start_tangent[0] * distance_cursor,
                    start_point[1] - start_tangent[1] * distance_cursor,
                ),
                start_tangent,
            )
        )
        distance_cursor += _ANCHOR_SPACING_M
    end_extension: list[tuple[float, Point2, Point2]] = []
    distance_cursor = _ANCHOR_SPACING_M
    while distance_cursor <= extension_length + _EPS:
        end_extension.append(
            (
                end_s + distance_cursor,
                (
                    end_point[0] + end_tangent[0] * distance_cursor,
                    end_point[1] + end_tangent[1] * distance_cursor,
                ),
                end_tangent,
            )
        )
        distance_cursor += _ANCHOR_SPACING_M
    return tuple(reversed(start_extension)) + tuple(anchors) + tuple(end_extension)


def _segment_tangent(a: Point2, b: Point2) -> Point2:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    norm = math.hypot(dx, dy)
    if norm <= _EPS:
        return (1.0, 0.0)
    return (dx / norm, dy / norm)
