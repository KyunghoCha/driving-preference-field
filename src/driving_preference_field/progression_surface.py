from __future__ import annotations

"""Current progression surface implementation.

This module treats progression guides as the control structure for a continuous
local-space coordinate field. The runtime evaluates one pooled blended
coordinate field across all progression anchors:

    progression_tilted(p)
      = support_mod * alignment_mod * (T(|n_hat|) + gain * L(u))

Anchor weights are computed globally, a provisional pooled progress estimate is
used to apply soft progress gating, and the final progress coordinate field is
blended across the whole anchor pool. The exported transverse term is then read
directly from the progression-guide geometry itself by projecting onto the
nearest resampled guide segment. Exact formulas here are current implementation
details, not the canonical design contract.
README plus the bilingual current formula references under
docs/en/reference/current_formula_reference.md and
docs/ko/reference/current_formula_reference.md must move with this module when
the implementation changes.
"""

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from .config import FieldConfig, ProgressionConfig, SurfaceTuningConfig
from .contracts import Point2, QueryContext, SemanticInputSnapshot, StateSample
from .geometry import clamp, polyline_length

_QUERY_BATCH_SIZE = 4096
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
    guides: tuple[SurfaceGuide, ...]
    guide_ids: tuple[str, ...]
    guide_anchor_ranges: tuple[tuple[int, int], ...]
    guide_progress_extents: tuple[tuple[float, float], ...]
    anchor_points: np.ndarray
    anchor_tangents: np.ndarray
    anchor_normals: np.ndarray
    anchor_cumulative_s: np.ndarray
    anchor_guide_lengths: np.ndarray
    anchor_guide_weights: np.ndarray
    anchor_confidences: np.ndarray
    anchor_guide_indices: np.ndarray
    segment_starts: np.ndarray
    segment_vectors: np.ndarray
    segment_lengths_sq: np.ndarray
    segment_normals: np.ndarray


@dataclass(frozen=True)
class PooledBlendResult:
    s_hat: np.ndarray
    n_hat: np.ndarray
    tangent_hat: np.ndarray
    support_sum: np.ndarray
    support_mod: np.ndarray
    alignment_mod: np.ndarray
    longitudinal_component: np.ndarray
    transverse_component: np.ndarray
    score: np.ndarray
    effective_anchor_count: np.ndarray
    anchor_count: int
    guide_support_sums: np.ndarray

class ProgressionSurfaceRuntime:
    """Cached runtime view over the current progression field implementation."""

    def __init__(
        self,
        snapshot: SemanticInputSnapshot,
        context: QueryContext,
        *,
        config: FieldConfig,
    ) -> None:
        self._snapshot = snapshot
        self._context = context
        self._field_config = config
        self._config = config.progression
        self._surface_tuning = config.surface_tuning
        self._surface = _surface_index(snapshot, self._surface_tuning)
        self._ego_s_hat = (
            _pooled_ego_s_hat(self._surface, context, self._config, self._surface_tuning)
            if self._config.longitudinal_frame == "ego_relative"
            else None
        )

    @property
    def surface(self) -> SurfaceIndex:
        return self._surface

    @property
    def config(self) -> ProgressionConfig:
        return self._config

    @property
    def field_config(self) -> FieldConfig:
        return self._field_config

    @property
    def surface_tuning(self) -> SurfaceTuningConfig:
        return self._surface_tuning

    def query_state(self, state: StateSample) -> dict[str, object]:
        if self._config.support_ceiling <= 0.0 or self._surface.anchor_points.size == 0:
            return {
                "score": 0.0,
                "anchor_count": 0,
                "effective_anchor_count": 0,
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
            arrays["_guide_support_sums"][:, 0],
        )
        return {
            "score": float(arrays["score"][0]),
            "anchor_count": int(arrays["anchor_count"][0]),
            "effective_anchor_count": int(arrays["effective_anchor_count"][0]),
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
                "anchor_count": empty.astype(int),
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
            "anchor_count": [],
            "effective_anchor_count": [],
        }
        internal_chunks: dict[str, list[np.ndarray]] = {
            "_guide_support_sums": [],
        }

        for start in range(0, point_count, _QUERY_BATCH_SIZE):
            stop = min(point_count, start + _QUERY_BATCH_SIZE)
            pooled = _pooled_blend_result(
                self._surface,
                x_values[start:stop],
                y_values[start:stop],
                heading_yaws[start:stop],
                config=self._config,
                tuning=self._surface_tuning,
                ego_s_hat=self._ego_s_hat,
            )
            chunks["score"].append(pooled.score)
            chunks["s_hat"].append(pooled.s_hat)
            chunks["n_hat"].append(pooled.n_hat)
            chunks["support_sum"].append(pooled.support_sum)
            chunks["support_mod"].append(pooled.support_mod)
            chunks["alignment_mod"].append(pooled.alignment_mod)
            chunks["longitudinal_component"].append(pooled.longitudinal_component)
            chunks["transverse_component"].append(pooled.transverse_component)
            chunks["anchor_count"].append(np.full((stop - start,), pooled.anchor_count, dtype=int))
            chunks["effective_anchor_count"].append(pooled.effective_anchor_count)
            if include_internal:
                internal_chunks["_guide_support_sums"].append(pooled.guide_support_sums)

        result = {name: np.concatenate(parts) for name, parts in chunks.items()}
        if include_internal:
            result["_guide_support_sums"] = np.concatenate(internal_chunks["_guide_support_sums"], axis=1)
        return result


def build_progression_surface_runtime(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig,
) -> ProgressionSurfaceRuntime:
    return ProgressionSurfaceRuntime(snapshot, context, config=config)


def progression_surface_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig,
) -> dict[str, object]:
    if config.progression.support_ceiling <= 0.0:
        return {
            "score": 0.0,
            "anchor_count": 0,
            "effective_anchor_count": 0,
            "support_sum": 0.0,
            "support_mod": 0.0,
            "alignment_mod": 0.0,
            "longitudinal_component": 0.0,
            "transverse_component": 0.0,
            "s_hat": 0.0,
            "n_hat": 0.0,
            "blended_progress": 0.0,
            "dominant_guides": (),
            "longitudinal_frame": config.progression.longitudinal_frame,
        }
    runtime = build_progression_surface_runtime(snapshot, context, config=config)
    return runtime.query_state(state)


def progression_surface_grid(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
) -> np.ndarray:
    runtime = build_progression_surface_runtime(snapshot, context, config=config)
    return runtime.query_grid(x_coords, y_coords)["score"]


def progression_surface_grid_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
) -> dict[str, np.ndarray]:
    runtime = build_progression_surface_runtime(snapshot, context, config=config)
    return runtime.query_grid(x_coords, y_coords)


def _pooled_blend_result(
    surface: SurfaceIndex,
    x_values: np.ndarray,
    y_values: np.ndarray,
    heading_yaws: np.ndarray,
    *,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
    ego_s_hat: float | None,
) -> PooledBlendResult:
    anchor_count = int(surface.anchor_points.shape[0])
    if anchor_count == 0:
        zeros = np.zeros_like(x_values)
        guide_count = len(surface.guides)
        return PooledBlendResult(
            s_hat=zeros,
            n_hat=zeros,
            tangent_hat=np.zeros((x_values.size, 2), dtype=float),
            support_sum=zeros,
            support_mod=zeros,
            alignment_mod=zeros,
            longitudinal_component=zeros,
            transverse_component=zeros,
            score=zeros,
            effective_anchor_count=np.zeros_like(x_values, dtype=int),
            anchor_count=0,
            guide_support_sums=np.zeros((guide_count, x_values.size), dtype=float),
        )

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
    s_values = cumulative_s + tau

    sigma_t = np.maximum(tuning.min_sigma_t, guide_lengths * config.lookahead_scale * tuning.sigma_t_scale)
    sigma_n = max(tuning.min_sigma_n, config.transverse_scale * tuning.sigma_n_scale)
    raw0 = guide_weights * confidences * np.exp(
        -0.5 * (((tau / sigma_t) ** 2) + ((nu / sigma_n) ** 2))
    )
    support_sum0 = np.sum(raw0, axis=0)
    provisional_weights = np.where(
        support_sum0[None, :] > _EPS,
        raw0 / np.clip(support_sum0[None, :], _EPS, None),
        0.0,
    )
    s_hat0 = np.sum(provisional_weights * s_values, axis=0)
    progress_gate = np.exp(-0.5 * (((s_values - s_hat0[None, :]) / sigma_t) ** 2))
    raw = raw0 * progress_gate
    support_sum = np.sum(raw, axis=0)
    blend_weights = np.where(
        support_sum[None, :] > _EPS,
        raw / np.clip(support_sum[None, :], _EPS, None),
        0.0,
    )

    s_hat = np.sum(blend_weights * s_values, axis=0)
    tangent_hat = np.stack(
        (
            np.sum(blend_weights * tangent_x, axis=0),
            np.sum(blend_weights * tangent_y, axis=0),
        ),
        axis=1,
    )
    tangent_norm = np.linalg.norm(tangent_hat, axis=1, keepdims=True)
    tangent_hat = tangent_hat / np.clip(tangent_norm, _EPS, None)

    guide_mins = np.asarray([item[0] for item in surface.guide_progress_extents], dtype=float)
    guide_maxes = np.asarray([item[1] for item in surface.guide_progress_extents], dtype=float)
    s_min_hat = np.sum(blend_weights * guide_mins[surface.anchor_guide_indices][:, None], axis=0)
    s_max_hat = np.sum(blend_weights * guide_maxes[surface.anchor_guide_indices][:, None], axis=0)
    progress_span = np.maximum(s_max_hat - s_min_hat, _EPS)
    if config.longitudinal_frame == "local_absolute":
        u_value = np.clip((s_hat - s_min_hat) / progress_span, 0.0, 1.0)
    else:
        lookahead = _ego_relative_lookahead_array(progress_span, config, tuning)
        reference_s = float(ego_s_hat or 0.0)
        u_value = np.clip(np.maximum(0.0, s_hat - reference_s) / lookahead, 0.0, 1.0)

    # Read transverse directly from the nearest progression-guide geometry.
    # Progress ordering remains pooled across the full anchor set, but the
    # cross-section distance follows the guide structure itself instead of a
    # second pooled local-frame reconstruction.
    n_hat = _guide_geometry_signed_distance(surface, x_values, y_values)
    transverse_component = _transverse_value_array(np.abs(n_hat) / max(config.transverse_scale, _EPS), config)
    longitudinal_component = _longitudinal_value_array(u_value, config)

    heading_x = np.cos(heading_yaws)
    heading_y = np.sin(heading_yaws)
    alignment_quality = np.maximum(
        0.0,
        heading_x * tangent_hat[:, 0] + heading_y * tangent_hat[:, 1],
    )
    alignment_mod = tuning.alignment_base + tuning.alignment_range * alignment_quality

    clipped_confidence = np.minimum(confidences, max(config.support_ceiling, _EPS))
    support_quality = np.sum(blend_weights * clipped_confidence, axis=0) / max(config.support_ceiling, _EPS)
    support_mod = tuning.support_base + tuning.support_range * np.clip(support_quality, 0.0, 1.0)

    score = support_mod * alignment_mod * (
        transverse_component + config.longitudinal_gain * longitudinal_component
    )
    effective_anchor_count = np.sum(
        blend_weights > _EFFECTIVE_ANCHOR_WEIGHT_EPS,
        axis=0,
        dtype=int,
    )
    guide_support_sums = (
        np.stack(
            [np.sum(raw[start:stop], axis=0) for start, stop in surface.guide_anchor_ranges],
            axis=0,
        )
        if surface.guide_anchor_ranges
        else np.zeros((0, x_values.size), dtype=float)
    )
    return PooledBlendResult(
        s_hat=s_hat,
        n_hat=n_hat,
        tangent_hat=tangent_hat,
        support_sum=support_sum,
        support_mod=support_mod,
        alignment_mod=alignment_mod,
        longitudinal_component=longitudinal_component,
        transverse_component=transverse_component,
        score=score,
        effective_anchor_count=effective_anchor_count,
        anchor_count=anchor_count,
        guide_support_sums=guide_support_sums,
    )


def _dominant_guides(
    surface: SurfaceIndex,
    guide_support_sums: np.ndarray,
) -> tuple[tuple[str, float], ...]:
    ranked = sorted(
        zip(surface.guide_ids, guide_support_sums.tolist(), strict=False),
        key=lambda item: item[1],
        reverse=True,
    )
    return tuple(ranked[:3])


def _pooled_ego_s_hat(
    surface: SurfaceIndex,
    context: QueryContext,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
) -> float:
    return float(
        _pooled_blend_result(
            surface,
            np.asarray([context.ego_pose.x], dtype=float),
            np.asarray([context.ego_pose.y], dtype=float),
            np.asarray([context.ego_pose.yaw], dtype=float),
            config=config,
            tuning=tuning,
            ego_s_hat=None,
        ).s_hat[0]
    )

def _ego_relative_lookahead(
    progress_span: float,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
) -> float:
    return max(tuning.min_sigma_t, progress_span * config.lookahead_scale)


def _ego_relative_lookahead_array(
    progress_span: np.ndarray,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
) -> np.ndarray:
    return np.maximum(tuning.min_sigma_t, progress_span * config.lookahead_scale)


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


def _guide_geometry_signed_distance(
    surface: SurfaceIndex,
    x_values: np.ndarray,
    y_values: np.ndarray,
) -> np.ndarray:
    if surface.segment_starts.size == 0:
        return np.zeros_like(x_values)

    start_x = surface.segment_starts[:, 0][:, None]
    start_y = surface.segment_starts[:, 1][:, None]
    vector_x = surface.segment_vectors[:, 0][:, None]
    vector_y = surface.segment_vectors[:, 1][:, None]
    length_sq = surface.segment_lengths_sq[:, None]

    rel_x = x_values[None, :] - start_x
    rel_y = y_values[None, :] - start_y
    projection = np.clip((rel_x * vector_x + rel_y * vector_y) / np.clip(length_sq, _EPS, None), 0.0, 1.0)
    closest_x = start_x + projection * vector_x
    closest_y = start_y + projection * vector_y
    offset_x = x_values[None, :] - closest_x
    offset_y = y_values[None, :] - closest_y
    distance_sq = offset_x * offset_x + offset_y * offset_y

    normal_x = surface.segment_normals[:, 0][:, None]
    normal_y = surface.segment_normals[:, 1][:, None]
    signed_distance = offset_x * normal_x + offset_y * normal_y

    best_segment = np.argmin(distance_sq, axis=0)
    sample_indices = np.arange(x_values.size)
    return signed_distance[best_segment, sample_indices]


def _surface_index(snapshot: SemanticInputSnapshot, tuning: SurfaceTuningConfig) -> SurfaceIndex:
    return _surface_index_from_signature(_surface_signature(snapshot, tuning))


def _surface_signature(
    snapshot: SemanticInputSnapshot,
    tuning: SurfaceTuningConfig,
) -> tuple[tuple[object, ...], ...]:
    tuning_signature = (
        "__surface_tuning__",
        round(tuning.anchor_spacing_m, 6),
        round(tuning.spline_sample_density_m, 6),
        int(tuning.spline_min_subdivisions),
        round(tuning.end_extension_m, 6),
    )
    guide_signature = tuple(
        (
            guide.guide_id,
            tuple((round(point[0], 6), round(point[1], 6)) for point in guide.points),
            round(guide.weight, 6),
            round(float(guide.metadata.get("confidence", 1.0)), 6),
        )
        for guide in snapshot.progression_support.guides
    )
    return (tuning_signature, *guide_signature)


@lru_cache(maxsize=32)
def _surface_index_from_signature(signature: tuple[tuple[object, ...], ...]) -> SurfaceIndex:
    guides: list[SurfaceGuide] = []
    guide_ids: list[str] = []

    anchor_points: list[Point2] = []
    anchor_tangents: list[Point2] = []
    anchor_normals: list[Point2] = []
    anchor_cumulative_s: list[float] = []
    anchor_guide_lengths: list[float] = []
    anchor_guide_weights: list[float] = []
    anchor_confidences: list[float] = []
    anchor_guide_indices: list[int] = []
    guide_anchor_ranges: list[tuple[int, int]] = []
    guide_progress_extents: list[tuple[float, float]] = []

    tuning_marker = signature[0]
    if not tuning_marker or tuning_marker[0] != "__surface_tuning__":
        raise ValueError("surface signature must include tuning header")
    tuning = SurfaceTuningConfig(
        anchor_spacing_m=float(tuning_marker[1]),
        spline_sample_density_m=float(tuning_marker[2]),
        spline_min_subdivisions=int(tuning_marker[3]),
        end_extension_m=float(tuning_marker[4]),
    )

    for guide_id, points_payload, weight, confidence in signature[1:]:
        points = tuple((float(x), float(y)) for x, y in points_payload)
        smooth_points = _smooth_resampled_points(points, tuning)
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
        guides.append(guide)
        guide_ids.append(guide.guide_id)
        guide_index = len(guides) - 1
        guide_anchor_start = len(anchor_points)
        for cumulative_s, point, tangent in _anchor_points_with_continuation(
            smooth_points,
            extension_length=tuning.end_extension_m,
            spacing=tuning.anchor_spacing_m,
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
        guide_anchor_stop = len(anchor_points)
        guide_anchor_ranges.append((guide_anchor_start, guide_anchor_stop))
        if guide_anchor_stop == guide_anchor_start:
            guide_progress_extents.append((0.0, 0.0))
        else:
            guide_progress_extents.append(
                (
                    float(min(anchor_cumulative_s[guide_anchor_start:guide_anchor_stop])),
                    float(max(anchor_cumulative_s[guide_anchor_start:guide_anchor_stop])),
                )
            )

    if not anchor_points:
        return SurfaceIndex(
            guides=tuple(guides),
            guide_ids=tuple(guide_ids),
            guide_anchor_ranges=tuple(guide_anchor_ranges),
            guide_progress_extents=tuple(guide_progress_extents),
            anchor_points=np.zeros((0, 2), dtype=float),
            anchor_tangents=np.zeros((0, 2), dtype=float),
            anchor_normals=np.zeros((0, 2), dtype=float),
            anchor_cumulative_s=np.zeros((0,), dtype=float),
            anchor_guide_lengths=np.zeros((0,), dtype=float),
            anchor_guide_weights=np.zeros((0,), dtype=float),
            anchor_confidences=np.zeros((0,), dtype=float),
            anchor_guide_indices=np.zeros((0,), dtype=int),
            segment_starts=np.zeros((0, 2), dtype=float),
            segment_vectors=np.zeros((0, 2), dtype=float),
            segment_lengths_sq=np.zeros((0,), dtype=float),
            segment_normals=np.zeros((0, 2), dtype=float),
        )

    cumulative_array = np.asarray(anchor_cumulative_s, dtype=float)
    segment_starts: list[Point2] = []
    segment_vectors: list[Point2] = []
    segment_lengths_sq: list[float] = []
    segment_normals: list[Point2] = []
    for start, stop in guide_anchor_ranges:
        if stop - start < 2:
            continue
        for anchor_index in range(start, stop - 1):
            start_point = anchor_points[anchor_index]
            end_point = anchor_points[anchor_index + 1]
            vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])
            length_sq = vector[0] * vector[0] + vector[1] * vector[1]
            if length_sq <= _EPS:
                continue
            inv_length = 1.0 / math.sqrt(length_sq)
            tangent = (vector[0] * inv_length, vector[1] * inv_length)
            normal = (-tangent[1], tangent[0])
            segment_starts.append(start_point)
            segment_vectors.append(vector)
            segment_lengths_sq.append(length_sq)
            segment_normals.append(normal)
    return SurfaceIndex(
        guides=tuple(guides),
        guide_ids=tuple(guide_ids),
        guide_anchor_ranges=tuple(guide_anchor_ranges),
        guide_progress_extents=tuple(guide_progress_extents),
        anchor_points=np.asarray(anchor_points, dtype=float),
        anchor_tangents=np.asarray(anchor_tangents, dtype=float),
        anchor_normals=np.asarray(anchor_normals, dtype=float),
        anchor_cumulative_s=cumulative_array,
        anchor_guide_lengths=np.asarray(anchor_guide_lengths, dtype=float),
        anchor_guide_weights=np.asarray(anchor_guide_weights, dtype=float),
        anchor_confidences=np.asarray(anchor_confidences, dtype=float),
        anchor_guide_indices=np.asarray(anchor_guide_indices, dtype=int),
        segment_starts=np.asarray(segment_starts, dtype=float),
        segment_vectors=np.asarray(segment_vectors, dtype=float),
        segment_lengths_sq=np.asarray(segment_lengths_sq, dtype=float),
        segment_normals=np.asarray(segment_normals, dtype=float),
    )


def _smooth_resampled_points(points: tuple[Point2, ...], tuning: SurfaceTuningConfig) -> tuple[Point2, ...]:
    if len(points) < 2:
        return points
    if len(points) == 2:
        return _arc_length_resample(points, spacing=tuning.anchor_spacing_m)

    dense: list[Point2] = []
    padded = (_reflect_endpoint(points[0], points[1]),) + points + (_reflect_endpoint(points[-1], points[-2]),)
    for index in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[index - 1], padded[index], padded[index + 1], padded[index + 2]
        subdivisions = max(
            tuning.spline_min_subdivisions,
            int(math.ceil(max(_distance(p1, p2), _EPS) / tuning.spline_sample_density_m)),
        )
        for step in range(subdivisions):
            u_value = step / subdivisions
            dense.append(_centripetal_catmull_rom_point(p0, p1, p2, p3, u_value))
    dense.append(points[-1])
    return _arc_length_resample(tuple(dense), spacing=tuning.anchor_spacing_m)


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
    spacing: float,
) -> tuple[tuple[float, Point2, Point2], ...]:
    anchors = list(_anchor_points(points))
    if not anchors:
        return ()
    start_s, start_point, start_tangent = anchors[0]
    end_s, end_point, end_tangent = anchors[-1]

    start_extension: list[tuple[float, Point2, Point2]] = []
    distance_cursor = spacing
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
        distance_cursor += spacing
    end_extension: list[tuple[float, Point2, Point2]] = []
    distance_cursor = spacing
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
        distance_cursor += spacing
    return tuple(reversed(start_extension)) + tuple(anchors) + tuple(end_extension)


def _segment_tangent(a: Point2, b: Point2) -> Point2:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    norm = math.hypot(dx, dy)
    if norm <= _EPS:
        return (1.0, 0.0)
    return (dx / norm, dy / norm)
