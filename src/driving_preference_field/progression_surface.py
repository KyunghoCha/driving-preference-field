from __future__ import annotations

"""Current progression surface implementation.

This module treats progression guides as the control structure for a continuous
local-space coordinate field. The runtime first evaluates guide-local blended
coordinates and scores, then selects a pointwise max envelope over the local
map:

    progression_tilted(p)
      = max_g support_mod_g * alignment_mod_g * (T(|n_hat_g|) + gain * L(u_g))

Guide-local support and coordinates come from Gaussian anchor weights. The
exact formula here is a current implementation detail, not the canonical design
contract. README plus the bilingual current formula references under
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
_TRANSVERSE_HANDOFF_SUPPORT_RATIO = 0.25
_TRANSVERSE_HANDOFF_SCORE_DELTA = 0.20
_TRANSVERSE_HANDOFF_TEMPERATURE = 0.05


@dataclass(frozen=True)
class SurfaceGuide:
    guide_id: str
    points: tuple[Point2, ...]
    distance_points: tuple[Point2, ...]
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


@dataclass(frozen=True)
class GuideBlendResult:
    guide_index: int
    guide_id: str
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
        self._ego_s_hat_by_guide = (
            _ego_s_hat_by_guide(self._surface, context, self._config, self._surface_tuning)
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
            arrays["_guide_scores"][:, 0],
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
            "_guide_scores": [],
            "_guide_support_sums": [],
        }

        for start in range(0, point_count, _QUERY_BATCH_SIZE):
            stop = min(point_count, start + _QUERY_BATCH_SIZE)
            guide_results = _guide_local_results(
                self._surface,
                x_values[start:stop],
                y_values[start:stop],
                heading_yaws[start:stop],
                config=self._config,
                tuning=self._surface_tuning,
                ego_s_hat_by_guide=self._ego_s_hat_by_guide,
            )
            selected = _select_dominant_guide(guide_results)
            chunks["score"].append(selected["score"])
            chunks["s_hat"].append(selected["s_hat"])
            chunks["n_hat"].append(selected["n_hat"])
            chunks["support_sum"].append(selected["support_sum"])
            chunks["support_mod"].append(selected["support_mod"])
            chunks["alignment_mod"].append(selected["alignment_mod"])
            chunks["longitudinal_component"].append(selected["longitudinal_component"])
            chunks["transverse_component"].append(selected["transverse_component"])
            chunks["anchor_count"].append(selected["anchor_count"])
            chunks["effective_anchor_count"].append(selected["effective_anchor_count"])
            if include_internal:
                internal_chunks["_guide_scores"].append(selected["guide_scores"])
                internal_chunks["_guide_support_sums"].append(selected["guide_support_sums"])

        result = {name: np.concatenate(parts) for name, parts in chunks.items()}
        if include_internal:
            result["_guide_scores"] = np.concatenate(internal_chunks["_guide_scores"], axis=1)
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


def _guide_local_results(
    surface: SurfaceIndex,
    x_values: np.ndarray,
    y_values: np.ndarray,
    heading_yaws: np.ndarray,
    *,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
    ego_s_hat_by_guide: tuple[float, ...] | None,
) -> tuple[GuideBlendResult, ...]:
    return tuple(
        _guide_local_result(
            surface,
            guide_index,
            x_values,
            y_values,
            heading_yaws,
            config=config,
            tuning=tuning,
            ego_s_hat=None if ego_s_hat_by_guide is None else ego_s_hat_by_guide[guide_index],
        )
        for guide_index in range(len(surface.guides))
    )


def _guide_local_result(
    surface: SurfaceIndex,
    guide_index: int,
    x_values: np.ndarray,
    y_values: np.ndarray,
    heading_yaws: np.ndarray,
    *,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
    ego_s_hat: float | None,
) -> GuideBlendResult:
    guide = surface.guides[guide_index]
    start, stop = surface.guide_anchor_ranges[guide_index]
    anchor_count = stop - start
    if anchor_count == 0:
        zeros = np.zeros_like(x_values)
        tangent_hat = np.zeros((x_values.size, 2), dtype=float)
        return GuideBlendResult(
            guide_index=guide_index,
            guide_id=guide.guide_id,
            s_hat=zeros,
            n_hat=zeros,
            tangent_hat=tangent_hat,
            support_sum=zeros,
            support_mod=zeros,
            alignment_mod=zeros,
            longitudinal_component=zeros,
            transverse_component=zeros,
            score=zeros,
            effective_anchor_count=np.zeros_like(x_values, dtype=int),
            anchor_count=0,
        )

    points_x = surface.anchor_points[start:stop, 0][:, None]
    points_y = surface.anchor_points[start:stop, 1][:, None]
    dx = x_values[None, :] - points_x
    dy = y_values[None, :] - points_y

    tangent_x = surface.anchor_tangents[start:stop, 0][:, None]
    tangent_y = surface.anchor_tangents[start:stop, 1][:, None]
    normal_x = surface.anchor_normals[start:stop, 0][:, None]
    normal_y = surface.anchor_normals[start:stop, 1][:, None]
    cumulative_s = surface.anchor_cumulative_s[start:stop][:, None]
    guide_lengths = surface.anchor_guide_lengths[start:stop][:, None]
    guide_weights = surface.anchor_guide_weights[start:stop][:, None]
    confidences = surface.anchor_confidences[start:stop][:, None]

    tau = dx * tangent_x + dy * tangent_y
    nu = dx * normal_x + dy * normal_y

    sigma_t = np.maximum(tuning.min_sigma_t, guide_lengths * config.lookahead_scale * tuning.sigma_t_scale)
    sigma_n = max(tuning.min_sigma_n, config.transverse_scale * tuning.sigma_n_scale)
    raw_weights = guide_weights * confidences * np.exp(
        -0.5 * (((tau / sigma_t) ** 2) + ((nu / sigma_n) ** 2))
    )
    support_sum = np.sum(raw_weights, axis=0)
    blend_weights = raw_weights / np.clip(support_sum, _EPS, None)

    s_values = cumulative_s + tau
    s_hat = np.sum(blend_weights * s_values, axis=0)
    n_hat = _unsigned_distance_to_polyline(guide.distance_points, x_values, y_values)
    tangent_hat = np.stack(
        (
            np.sum(blend_weights * tangent_x, axis=0),
            np.sum(blend_weights * tangent_y, axis=0),
        ),
        axis=1,
    )
    tangent_norm = np.linalg.norm(tangent_hat, axis=1, keepdims=True)
    tangent_hat = tangent_hat / np.clip(tangent_norm, _EPS, None)

    # Cache guide progress extents once in the surface index instead of
    # rescanning each guide's anchor slice on every query.
    guide_min_progress_extent, guide_max_progress_extent = surface.guide_progress_extents[guide_index]
    progress_span = max(guide_max_progress_extent - guide_min_progress_extent, _EPS)
    if config.longitudinal_frame == "local_absolute":
        u_value = np.clip((s_hat - guide_min_progress_extent) / progress_span, 0.0, 1.0)
    else:
        lookahead = max(_ego_relative_lookahead(progress_span, config, tuning), _EPS)
        reference_s = float(ego_s_hat or 0.0)
        u_value = np.clip(np.maximum(0.0, s_hat - reference_s) / lookahead, 0.0, 1.0)

    transverse_ratio = np.abs(n_hat) / max(config.transverse_scale, _EPS)
    transverse_component = _transverse_value_array(transverse_ratio, config)
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
    return GuideBlendResult(
        guide_index=guide_index,
        guide_id=guide.guide_id,
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
    )


def _select_dominant_guide(
    guide_results: tuple[GuideBlendResult, ...],
) -> dict[str, np.ndarray]:
    if not guide_results:
        zeros = np.zeros((0,), dtype=float)
        return {
            "score": zeros,
            "s_hat": zeros,
            "n_hat": zeros,
            "support_sum": zeros,
            "support_mod": zeros,
            "alignment_mod": zeros,
            "longitudinal_component": zeros,
            "transverse_component": zeros,
            "anchor_count": np.zeros((0,), dtype=int),
            "effective_anchor_count": np.zeros((0,), dtype=int),
            "guide_scores": np.zeros((0, 0), dtype=float),
            "guide_support_sums": np.zeros((0, 0), dtype=float),
        }

    stacked_transverse = np.stack([result.transverse_component for result in guide_results], axis=0)
    point_count = guide_results[0].score.size
    guide_scores = np.stack([result.score for result in guide_results], axis=0)
    guide_support_sums = np.stack([result.support_sum for result in guide_results], axis=0)

    best_indices = np.zeros(point_count, dtype=int)
    best_scores = guide_scores[0].copy()
    best_support = guide_support_sums[0].copy()
    for guide_index in range(1, len(guide_results)):
        scores = guide_scores[guide_index]
        supports = guide_support_sums[guide_index]
        better_score = scores > (best_scores + _EPS)
        equal_score = np.isclose(scores, best_scores, atol=_EPS, rtol=0.0)
        better_support = supports > (best_support + _EPS)
        take = better_score | (equal_score & better_support)
        best_indices = np.where(take, guide_index, best_indices)
        best_scores = np.where(take, scores, best_scores)
        best_support = np.where(take, supports, best_support)

    positions = np.arange(point_count)

    def _select(field_name: str) -> np.ndarray:
        stacked = np.stack([getattr(result, field_name) for result in guide_results], axis=0)
        return stacked[best_indices, positions]

    # Keep both counts so downstream diagnostics can distinguish "how many
    # anchors exist on the dominant guide" from "how many materially blended".
    selected_anchor_count = np.asarray(
        [guide_results[index].anchor_count for index in best_indices],
        dtype=int,
    )
    dominant_weight = np.zeros_like(guide_scores)
    dominant_weight[best_indices, positions] = 1.0
    candidate_mask = (
        guide_support_sums >= (_TRANSVERSE_HANDOFF_SUPPORT_RATIO * best_support[None, :])
    ) & (
        guide_scores >= (best_scores[None, :] - _TRANSVERSE_HANDOFF_SCORE_DELTA)
    )
    candidate_mask[best_indices, positions] = True
    scaled_score_delta = np.clip(
        (guide_scores - best_scores[None, :]) / _TRANSVERSE_HANDOFF_TEMPERATURE,
        -60.0,
        0.0,
    )
    transverse_weights = np.where(
        candidate_mask,
        guide_support_sums * np.exp(scaled_score_delta),
        0.0,
    )
    transverse_weight_sum = np.sum(transverse_weights, axis=0)
    normalized_transverse_weights = np.where(
        transverse_weight_sum[None, :] > _EPS,
        transverse_weights / np.clip(transverse_weight_sum[None, :], _EPS, None),
        dominant_weight,
    )
    smoothed_transverse = np.sum(normalized_transverse_weights * stacked_transverse, axis=0)

    return {
        "score": _select("score"),
        "s_hat": _select("s_hat"),
        "n_hat": _select("n_hat"),
        "support_sum": _select("support_sum"),
        "support_mod": _select("support_mod"),
        "alignment_mod": _select("alignment_mod"),
        "longitudinal_component": _select("longitudinal_component"),
        "transverse_component": smoothed_transverse,
        "anchor_count": selected_anchor_count,
        "effective_anchor_count": _select("effective_anchor_count").astype(int),
        "guide_scores": guide_scores,
        "guide_support_sums": guide_support_sums,
    }


def _dominant_guides(
    surface: SurfaceIndex,
    guide_scores: np.ndarray,
    guide_support_sums: np.ndarray,
) -> tuple[tuple[str, float, float], ...]:
    ranked = sorted(
        zip(surface.guide_ids, guide_scores.tolist(), guide_support_sums.tolist(), strict=False),
        key=lambda item: (item[1], item[2]),
        reverse=True,
    )
    return tuple(ranked[:3])


def _ego_s_hat_by_guide(
    surface: SurfaceIndex,
    context: QueryContext,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
) -> tuple[float, ...]:
    return tuple(
        float(
            _guide_local_result(
                surface,
                guide_index,
                np.asarray([context.ego_pose.x], dtype=float),
                np.asarray([context.ego_pose.y], dtype=float),
                np.asarray([context.ego_pose.yaw], dtype=float),
                config=config,
                tuning=tuning,
                ego_s_hat=None,
            ).s_hat[0]
        )
        for guide_index in range(len(surface.guides))
    )

def _ego_relative_lookahead(
    progress_span: float,
    config: ProgressionConfig,
    tuning: SurfaceTuningConfig,
) -> float:
    return max(tuning.min_sigma_t, progress_span * config.lookahead_scale)


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


def _unsigned_distance_to_polyline(
    polyline: tuple[Point2, ...],
    x_values: np.ndarray,
    y_values: np.ndarray,
) -> np.ndarray:
    if len(polyline) < 2:
        return np.zeros_like(x_values)

    points = np.asarray(polyline, dtype=float)
    starts = points[:-1]
    ends = points[1:]
    seg = ends - starts
    seg_len_sq = np.sum(seg * seg, axis=1)
    valid = seg_len_sq > _EPS
    if not np.any(valid):
        return np.zeros_like(x_values)

    starts = starts[valid]
    seg = seg[valid]
    seg_len_sq = seg_len_sq[valid]

    dx = x_values[None, :] - starts[:, 0][:, None]
    dy = y_values[None, :] - starts[:, 1][:, None]
    t = np.clip((dx * seg[:, 0][:, None] + dy * seg[:, 1][:, None]) / seg_len_sq[:, None], 0.0, 1.0)
    proj_x = starts[:, 0][:, None] + t * seg[:, 0][:, None]
    proj_y = starts[:, 1][:, None] + t * seg[:, 1][:, None]

    offset_x = x_values[None, :] - proj_x
    offset_y = y_values[None, :] - proj_y
    dist_sq = offset_x * offset_x + offset_y * offset_y
    return np.sqrt(np.min(dist_sq, axis=0))


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
            distance_points=_distance_points_with_continuation(smooth_points, tuning),
            guide_length=guide_length,
            weight=float(weight),
            confidence=float(confidence),
        )
        guides.append(guide)
        guide_ids.append(guide.guide_id)
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
        )

    cumulative_array = np.asarray(anchor_cumulative_s, dtype=float)
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


def _distance_points_with_continuation(
    points: tuple[Point2, ...],
    tuning: SurfaceTuningConfig,
) -> tuple[Point2, ...]:
    spacing = max(tuning.anchor_spacing_m * 0.25, 0.025)
    dense_points = _arc_length_resample(points, spacing=spacing)
    if len(dense_points) < 2 or tuning.end_extension_m <= _EPS:
        return dense_points

    start_tangent = _segment_tangent(dense_points[0], dense_points[1])
    end_tangent = _segment_tangent(dense_points[-2], dense_points[-1])

    start_extension: list[Point2] = []
    distance_cursor = spacing
    while distance_cursor <= tuning.end_extension_m + _EPS:
        start_extension.append(
            (
                dense_points[0][0] - start_tangent[0] * distance_cursor,
                dense_points[0][1] - start_tangent[1] * distance_cursor,
            )
        )
        distance_cursor += spacing

    end_extension: list[Point2] = []
    distance_cursor = spacing
    while distance_cursor <= tuning.end_extension_m + _EPS:
        end_extension.append(
            (
                dense_points[-1][0] + end_tangent[0] * distance_cursor,
                dense_points[-1][1] + end_tangent[1] * distance_cursor,
            )
        )
        distance_cursor += spacing

    return (*reversed(start_extension), *dense_points, *end_extension)


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
