from __future__ import annotations

"""Current progression surface implementation.

This module turns progression and branch guides into a local-map-wide scalar
field by first blending local coordinates and then evaluating an additive
transverse-plus-longitudinal score:

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
from .geometry import clamp, dot, normalize, polyline_length

_ANCHOR_SPACING_M = 0.20
_SPLINE_SAMPLE_DENSITY_M = 0.05
_SPLINE_MIN_SUBDIVISIONS = 8
_MIN_SIGMA_T = 0.40
_MIN_SIGMA_N = 0.35
_SIGMA_T_SCALE = 0.35
_SIGMA_N_SCALE = 1.50
_TOP_K_ANCHORS = 12
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
            "blended_progress": 0.0,
            "dominant_guides": (),
            "longitudinal_frame": config.longitudinal_frame,
        }

    surface = _surface_index(snapshot)
    if surface.anchor_points.size == 0:
        return {
            "score": 0.0,
            "anchor_count": 0,
            "support_sum": 0.0,
            "support_mod": 0.0,
            "alignment_mod": 0.0,
            "longitudinal_component": 0.0,
            "transverse_component": 0.0,
            "blended_progress": 0.0,
            "dominant_guides": (),
            "longitudinal_frame": config.longitudinal_frame,
        }

    x_values = np.asarray([state.x], dtype=float)
    y_values = np.asarray([state.y], dtype=float)
    blend = _blend_coordinates(surface, x_values, y_values, config)
    longitudinal_component, transverse_component, support_mod, alignment_mod = _surface_components(
        surface,
        blend,
        config=config,
        heading_yaws=np.asarray([state.yaw], dtype=float),
        ego_s_hat=_ego_s_hat(surface, context, config) if config.longitudinal_frame == "ego_relative" else None,
    )
    score = float(
        support_mod[0]
        * alignment_mod[0]
        * (transverse_component[0] + config.longitudinal_gain * longitudinal_component[0])
    )
    dominant_guides = _dominant_guides(surface, blend.anchor_indices[:, 0], blend.blend_weights[:, 0])
    return {
        "score": score,
        "anchor_count": blend.anchor_count,
        "support_sum": float(blend.support_sum[0]),
        "support_mod": float(support_mod[0]),
        "alignment_mod": float(alignment_mod[0]),
        "longitudinal_component": float(longitudinal_component[0]),
        "transverse_component": float(transverse_component[0]),
        "blended_progress": float(blend.s_hat[0]),
        "dominant_guides": dominant_guides,
        "longitudinal_frame": config.longitudinal_frame,
    }


def progression_surface_grid(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: ProgressionConfig,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
) -> np.ndarray:
    if config.support_ceiling <= 0.0:
        return np.zeros((len(y_coords), len(x_coords)), dtype=float)

    surface = _surface_index(snapshot)
    if surface.anchor_points.size == 0:
        return np.zeros((len(y_coords), len(x_coords)), dtype=float)

    grid_x, grid_y = np.meshgrid(x_coords, y_coords)
    flat_x = grid_x.ravel()
    flat_y = grid_y.ravel()
    yaw_values = np.full_like(flat_x, context.ego_pose.yaw, dtype=float)
    blend = _blend_coordinates(surface, flat_x, flat_y, config)
    longitudinal_component, transverse_component, support_mod, alignment_mod = _surface_components(
        surface,
        blend,
        config=config,
        heading_yaws=yaw_values,
        ego_s_hat=_ego_s_hat(surface, context, config) if config.longitudinal_frame == "ego_relative" else None,
    )
    score = support_mod * alignment_mod * (
        transverse_component + config.longitudinal_gain * longitudinal_component
    )
    return score.reshape((len(y_coords), len(x_coords)))


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

    s_max = max(surface.max_guide_length, _EPS)
    if config.longitudinal_frame == "local_absolute":
        u_value = np.clip(blend.s_hat / s_max, 0.0, 1.0)
    else:
        lookahead = max(_ego_relative_lookahead(surface, config), _EPS)
        reference_s = float(ego_s_hat or 0.0)
        u_value = np.clip(np.maximum(0.0, blend.s_hat - reference_s) / lookahead, 0.0, 1.0)

    transverse_ratio = blend.n_hat / max(config.transverse_scale, _EPS)
    transverse_component = _transverse_value_array(transverse_ratio, config)
    longitudinal_component = _longitudinal_value_array(u_value, config)

    heading_x = np.cos(heading_yaws)
    heading_y = np.sin(heading_yaws)
    alignment = np.maximum(
        0.0,
        heading_x * blend.tangent_hat[:, 0] + heading_y * blend.tangent_hat[:, 1],
    )
    alignment_mod = 0.85 + 0.15 * alignment

    support_ratio = np.clip(
        blend.support_sum / max(config.support_ceiling, _EPS),
        0.0,
        1.0,
    )
    support_mod = 0.85 + 0.15 * support_ratio
    return longitudinal_component, transverse_component, support_mod, alignment_mod


def _blend_coordinates(
    surface: SurfaceIndex,
    x_values: np.ndarray,
    y_values: np.ndarray,
    config: ProgressionConfig,
) -> BlendResult:
    points_x = surface.anchor_points[:, 0][:, None]
    points_y = surface.anchor_points[:, 1][:, None]
    dx = x_values[None, :] - points_x
    dy = y_values[None, :] - points_y
    distance_sq = dx * dx + dy * dy

    anchor_count = surface.anchor_points.shape[0]
    selected = min(_TOP_K_ANCHORS, anchor_count)
    if selected == anchor_count:
        anchor_indices = np.repeat(np.arange(anchor_count, dtype=int)[:, None], x_values.size, axis=1)
    else:
        anchor_indices = np.argpartition(distance_sq, kth=selected - 1, axis=0)[:selected, :]

    dx_sel = np.take_along_axis(dx, anchor_indices, axis=0)
    dy_sel = np.take_along_axis(dy, anchor_indices, axis=0)
    tangent_x = surface.anchor_tangents[:, 0][anchor_indices]
    tangent_y = surface.anchor_tangents[:, 1][anchor_indices]
    normal_x = surface.anchor_normals[:, 0][anchor_indices]
    normal_y = surface.anchor_normals[:, 1][anchor_indices]
    cumulative_s = surface.anchor_cumulative_s[anchor_indices]
    guide_lengths = surface.anchor_guide_lengths[anchor_indices]
    guide_weights = surface.anchor_guide_weights[anchor_indices]
    confidences = surface.anchor_confidences[anchor_indices]

    tau = dx_sel * tangent_x + dy_sel * tangent_y
    nu = dx_sel * normal_x + dy_sel * normal_y

    sigma_t = np.maximum(_MIN_SIGMA_T, guide_lengths * config.lookahead_scale * _SIGMA_T_SCALE)
    sigma_n = max(_MIN_SIGMA_N, config.transverse_scale * _SIGMA_N_SCALE)
    raw_weights = guide_weights * confidences * np.exp(
        -0.5 * (((tau / sigma_t) ** 2) + ((nu / sigma_n) ** 2))
    )
    support_sum = np.sum(raw_weights, axis=0)
    blend_weights = raw_weights / np.clip(support_sum, _EPS, None)

    s_values = np.clip(cumulative_s + tau, 0.0, guide_lengths)
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
        anchor_count=selected,
    )


def _dominant_guides(
    surface: SurfaceIndex,
    anchor_indices: np.ndarray,
    blend_weights: np.ndarray,
) -> tuple[tuple[str, float], ...]:
    per_guide: dict[str, float] = {}
    for anchor_index, weight in zip(anchor_indices.tolist(), blend_weights.tolist(), strict=False):
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
    return max(_MIN_SIGMA_T, surface.max_guide_length * config.lookahead_scale)


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
        for cumulative_s, point, tangent in _anchor_points(smooth_points):
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
            anchor_points=np.zeros((0, 2), dtype=float),
            anchor_tangents=np.zeros((0, 2), dtype=float),
            anchor_normals=np.zeros((0, 2), dtype=float),
            anchor_cumulative_s=np.zeros((0,), dtype=float),
            anchor_guide_lengths=np.zeros((0,), dtype=float),
            anchor_guide_weights=np.zeros((0,), dtype=float),
            anchor_confidences=np.zeros((0,), dtype=float),
            anchor_guide_indices=np.zeros((0,), dtype=int),
        )

    return SurfaceIndex(
        signature=signature,
        guides=tuple(guides),
        guide_points=tuple(guide_points),
        guide_ids=tuple(guide_ids),
        max_guide_length=max(anchor_guide_lengths),
        anchor_points=np.asarray(anchor_points, dtype=float),
        anchor_tangents=np.asarray(anchor_tangents, dtype=float),
        anchor_normals=np.asarray(anchor_normals, dtype=float),
        anchor_cumulative_s=np.asarray(anchor_cumulative_s, dtype=float),
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
            tangent = normalize((points[1][0] - point[0], points[1][1] - point[1]))
        elif index == len(points) - 1:
            tangent = normalize((point[0] - points[index - 1][0], point[1] - points[index - 1][1]))
        else:
            tangent = normalize(
                (
                    points[index + 1][0] - points[index - 1][0],
                    points[index + 1][1] - points[index - 1][1],
                )
            )
        anchors.append((cumulative[index], point, tangent))
    return tuple(anchors)
