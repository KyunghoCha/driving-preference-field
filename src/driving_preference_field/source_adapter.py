from __future__ import annotations

"""Generic source adapter for canonical semantic snapshot generation.

This module defines a reference adapter that reads a generic local semantic map
fixture and translates it into the canonical SemanticInputSnapshot +
QueryContext contract. The input shape stays source-agnostic on purpose: it is
a generic external-like schema rather than a downstream-specific wire format.
"""

import json
import math
from pathlib import Path
from typing import Any

import yaml

from .contracts import (
    BoundaryInteriorSupport,
    DirectedPolyline,
    DrivableSupport,
    ExceptionLayerSupport,
    Point2,
    PolygonRegion,
    ProgressionSupport,
    QueryContext,
    QueryWindow,
    SemanticInputSnapshot,
    StateSample,
)
from .geometry import clamp, distance_point_to_polygon_boundary, point_in_polygon
from .toy_loader import summarize_snapshot


class GenericAdapterValidationError(ValueError):
    """Raised when a generic semantic input fixture fails validation."""


def _load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise GenericAdapterValidationError("generic adapter input must be a mapping at the top level")
    return dict(payload)


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise GenericAdapterValidationError(f"{key} must be a mapping")
    return dict(value)


def _optional_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise GenericAdapterValidationError(f"{key} must be a mapping when provided")
    return dict(value)


def _require_sequence(payload: dict[str, Any], key: str) -> list[Any]:
    if key not in payload:
        raise GenericAdapterValidationError(f"{key} is required")
    value = payload[key]
    if not isinstance(value, list):
        raise GenericAdapterValidationError(f"{key} must be a list")
    return list(value)


def _optional_sequence(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise GenericAdapterValidationError(f"{key} must be a list when provided")
    return list(value)


def _reject_removed_key(payload: dict[str, Any], key: str, *, message: str) -> None:
    if key in payload:
        raise GenericAdapterValidationError(message)


def _coerce_point(raw: Any, *, path: str) -> Point2:
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise GenericAdapterValidationError(f"{path} must be a 2-element point")
    try:
        return (float(raw[0]), float(raw[1]))
    except (TypeError, ValueError) as exc:
        raise GenericAdapterValidationError(f"{path} must contain numeric values") from exc


def _require_float(mapping: dict[str, Any], key: str, *, path: str) -> float:
    if key not in mapping:
        raise GenericAdapterValidationError(f"{path}.{key} is required")
    try:
        return float(mapping[key])
    except (TypeError, ValueError) as exc:
        raise GenericAdapterValidationError(f"{path}.{key} must be numeric") from exc


def _point_list(raw_points: Any, *, path: str, min_points: int) -> tuple[Point2, ...]:
    if not isinstance(raw_points, list):
        raise GenericAdapterValidationError(f"{path} must be a list of points")
    points = tuple(_coerce_point(item, path=f"{path}[{index}]") for index, item in enumerate(raw_points))
    if len(points) < min_points:
        raise GenericAdapterValidationError(f"{path} must contain at least {min_points} points")
    return points


def _merged_metadata(item: dict[str, Any], *, path: str) -> dict[str, Any]:
    metadata = dict(item.get("metadata", {}))
    if "branch_prior" in item or "branch_prior" in metadata:
        raise GenericAdapterValidationError(
            f"{path}.branch_prior is no longer supported; express split/merge as multiple progression_supports"
        )
    if "support_confidence" in item and "support_confidence" not in metadata:
        try:
            metadata["support_confidence"] = float(item["support_confidence"])
        except (TypeError, ValueError) as exc:
            raise GenericAdapterValidationError(f"{path}.support_confidence must be numeric") from exc
    return metadata


def _polygon_list(items: list[Any], *, key: str) -> tuple[PolygonRegion, ...]:
    regions: list[PolygonRegion] = []
    for index, raw_item in enumerate(items):
        if not isinstance(raw_item, dict):
            raise GenericAdapterValidationError(f"{key}[{index}] must be a mapping")
        item = dict(raw_item)
        regions.append(
            PolygonRegion(
                region_id=str(item.get("id", f"{key}_{index}")),
                points=_point_list(item.get("points"), path=f"{key}[{index}].points", min_points=3),
                severity=float(item.get("severity", 1.0)),
                hard=bool(item.get("hard", False)),
                influence_radius=float(item.get("influence_radius", 1.0)),
                metadata=_merged_metadata(item, path=f"{key}[{index}]"),
            )
        )
    return tuple(regions)


def _polyline_list(items: list[Any], *, key: str) -> tuple[DirectedPolyline, ...]:
    guides: list[DirectedPolyline] = []
    for index, raw_item in enumerate(items):
        if not isinstance(raw_item, dict):
            raise GenericAdapterValidationError(f"{key}[{index}] must be a mapping")
        item = dict(raw_item)
        guides.append(
            DirectedPolyline(
                guide_id=str(item.get("id", f"{key}_{index}")),
                points=_point_list(item.get("points"), path=f"{key}[{index}].points", min_points=2),
                weight=float(item.get("weight", 1.0)),
                metadata=_merged_metadata(item, path=f"{key}[{index}]"),
            )
        )
    return tuple(guides)


_GEOM_EPS = 1e-9
_RECONSTRUCTION_STEP_M = 0.4
_MIN_CENTERLINE_STEP_M = 0.1
_MAX_RECONSTRUCTION_STEPS = 128


def _sub(a: Point2, b: Point2) -> Point2:
    return (a[0] - b[0], a[1] - b[1])


def _add(a: Point2, b: Point2) -> Point2:
    return (a[0] + b[0], a[1] + b[1])


def _scale(v: Point2, scalar: float) -> Point2:
    return (v[0] * scalar, v[1] * scalar)


def _dot(a: Point2, b: Point2) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _cross(a: Point2, b: Point2) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _norm(v: Point2) -> float:
    return math.hypot(v[0], v[1])


def _normalize(v: Point2) -> Point2:
    length = _norm(v)
    if length <= _GEOM_EPS:
        return (0.0, 0.0)
    return (v[0] / length, v[1] / length)


def _perp(v: Point2) -> Point2:
    return (-v[1], v[0])


def _distance(a: Point2, b: Point2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _closed_polygon_segments(points: tuple[Point2, ...]) -> tuple[tuple[Point2, Point2], ...]:
    return tuple((points[index], points[(index + 1) % len(points)]) for index in range(len(points)))


def _point_to_segment_projection(point: Point2, start: Point2, end: Point2) -> tuple[Point2, float]:
    segment = _sub(end, start)
    seg_len_sq = _dot(segment, segment)
    if seg_len_sq <= _GEOM_EPS:
        return start, 0.0
    t = clamp(_dot(_sub(point, start), segment) / seg_len_sq, 0.0, 1.0)
    return _add(start, _scale(segment, t)), t


def _nearest_point_on_polygon_boundary(point: Point2, polygon: tuple[Point2, ...]) -> Point2:
    best_point = polygon[0]
    best_distance = math.inf
    for start, end in _closed_polygon_segments(polygon):
        projected, _ = _point_to_segment_projection(point, start, end)
        distance = _distance(point, projected)
        if distance < best_distance:
            best_distance = distance
            best_point = projected
    return best_point


def _polygon_centroid(points: tuple[Point2, ...]) -> Point2:
    area_twice = 0.0
    cx = 0.0
    cy = 0.0
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        cross = point[0] * next_point[1] - next_point[0] * point[1]
        area_twice += cross
        cx += (point[0] + next_point[0]) * cross
        cy += (point[1] + next_point[1]) * cross
    if abs(area_twice) <= _GEOM_EPS:
        return (
            sum(point[0] for point in points) / max(len(points), 1),
            sum(point[1] for point in points) / max(len(points), 1),
        )
    return (cx / (3.0 * area_twice), cy / (3.0 * area_twice))


def _polygon_is_convex(points: tuple[Point2, ...]) -> bool:
    signs: list[float] = []
    count = len(points)
    for index in range(count):
        a = points[index]
        b = points[(index + 1) % count]
        c = points[(index + 2) % count]
        cross = _cross(_sub(b, a), _sub(c, b))
        if abs(cross) <= _GEOM_EPS:
            continue
        signs.append(math.copysign(1.0, cross))
    if not signs:
        return True
    first = signs[0]
    return all(sign == first for sign in signs[1:])


def _pick_primary_drivable_region(regions: tuple[PolygonRegion, ...], ego_point: Point2) -> PolygonRegion:
    containing = [region for region in regions if point_in_polygon(ego_point, region.points)]
    if containing:
        return containing[0]
    return min(regions, key=lambda region: distance_point_to_polygon_boundary(ego_point, region.points))


def _line_segment_intersection_lambda(
    origin: Point2,
    direction: Point2,
    start: Point2,
    end: Point2,
) -> float | None:
    segment = _sub(end, start)
    denominator = _cross(direction, segment)
    if abs(denominator) <= _GEOM_EPS:
        return None
    offset = _sub(start, origin)
    line_lambda = _cross(offset, segment) / denominator
    segment_u = _cross(offset, direction) / denominator
    if -_GEOM_EPS <= segment_u <= 1.0 + _GEOM_EPS:
        return line_lambda
    return None


def _dedupe_sorted(values: list[float], *, tol: float = 1e-6) -> list[float]:
    deduped: list[float] = []
    for value in sorted(values):
        if not deduped or abs(value - deduped[-1]) > tol:
            deduped.append(value)
    return deduped


def _cross_section_lambdas(center: Point2, tangent: Point2, polygon: tuple[Point2, ...]) -> list[float]:
    normal = _perp(_normalize(tangent))
    if _norm(normal) <= _GEOM_EPS:
        raise GenericAdapterValidationError(
            "drivable-only reconstruction could not establish a valid cross-section normal"
        )
    lambdas: list[float] = []
    for start, end in _closed_polygon_segments(polygon):
        hit_lambda = _line_segment_intersection_lambda(center, normal, start, end)
        if hit_lambda is not None:
            lambdas.append(hit_lambda)
    return _dedupe_sorted(lambdas)


def _cross_section_hits(center: Point2, tangent: Point2, polygon: tuple[Point2, ...]) -> tuple[Point2, Point2]:
    normal = _perp(_normalize(tangent))
    lambdas = _cross_section_lambdas(center, tangent, polygon)
    negatives = [value for value in lambdas if value < -1e-6]
    positives = [value for value in lambdas if value > 1e-6]
    if not negatives or not positives:
        raise GenericAdapterValidationError(
            "drivable-only reconstruction is ambiguous or disconnected; provide progression_supports or global_plan_supports"
        )
    left_lambda = max(negatives)
    right_lambda = min(positives)
    left_hit = _add(center, _scale(normal, left_lambda))
    right_hit = _add(center, _scale(normal, right_lambda))
    return left_hit, right_hit


def _blend_tangent(base: Point2, future_anchor: Point2 | None, center: Point2) -> Point2:
    tangent = _normalize(base)
    if future_anchor is None:
        return tangent
    anchor_direction = _normalize(_sub(future_anchor, center))
    if _norm(anchor_direction) <= _GEOM_EPS:
        return tangent
    blended = _normalize(
        (
            0.7 * tangent[0] + 0.3 * anchor_direction[0],
            0.7 * tangent[1] + 0.3 * anchor_direction[1],
        )
    )
    return blended if _norm(blended) > _GEOM_EPS else tangent


def _initial_center_point(region: PolygonRegion, ego_pose: StateSample) -> Point2:
    if point_in_polygon(ego_pose.point, region.points):
        return ego_pose.point
    nearest = _nearest_point_on_polygon_boundary(ego_pose.point, region.points)
    centroid = _polygon_centroid(region.points)
    inward = _normalize(_sub(centroid, nearest))
    if _norm(inward) <= _GEOM_EPS:
        return nearest
    nudged = _add(nearest, _scale(inward, 0.05))
    return nudged if point_in_polygon(nudged, region.points) else nearest


def _reconstruct_centerline_from_drivable(
    drivable_regions: tuple[PolygonRegion, ...],
    *,
    ego_pose: StateSample,
    future_anchor: Point2 | None,
) -> tuple[Point2, ...]:
    if not drivable_regions:
        raise GenericAdapterValidationError(
            "drivable_regions are required when progression_supports and global_plan_supports are absent"
        )
    region = _pick_primary_drivable_region(drivable_regions, ego_pose.point)
    if future_anchor is None and not _polygon_is_convex(region.points):
        raise GenericAdapterValidationError(
            "drivable-only reconstruction is ambiguous or disconnected; provide progression_supports or global_plan_supports"
        )
    current_center = _initial_center_point(region, ego_pose)
    tangent = _blend_tangent((math.cos(ego_pose.yaw), math.sin(ego_pose.yaw)), future_anchor, current_center)
    reconstructed: list[Point2] = []

    for _ in range(_MAX_RECONSTRUCTION_STEPS):
        current_lambdas = _cross_section_lambdas(current_center, tangent, region.points)
        if future_anchor is None and len(current_lambdas) > 2:
            raise GenericAdapterValidationError(
                "drivable-only reconstruction is ambiguous or disconnected; provide progression_supports or global_plan_supports"
            )
        left_hit, right_hit = _cross_section_hits(current_center, tangent, region.points)
        midpoint = ((left_hit[0] + right_hit[0]) * 0.5, (left_hit[1] + right_hit[1]) * 0.5)
        if not reconstructed or _distance(midpoint, reconstructed[-1]) >= _MIN_CENTERLINE_STEP_M:
            reconstructed.append(midpoint)

        probe = _add(midpoint, _scale(tangent, _RECONSTRUCTION_STEP_M))
        if not point_in_polygon(probe, region.points):
            break
        probe_lambdas = _cross_section_lambdas(probe, tangent, region.points)
        if future_anchor is None and len(probe_lambdas) > 2:
            raise GenericAdapterValidationError(
                "drivable-only reconstruction is ambiguous or disconnected; provide progression_supports or global_plan_supports"
            )
        next_left, next_right = _cross_section_hits(probe, tangent, region.points)
        next_midpoint = ((next_left[0] + next_right[0]) * 0.5, (next_left[1] + next_right[1]) * 0.5)
        step_vector = _sub(next_midpoint, midpoint)
        if _norm(step_vector) < _MIN_CENTERLINE_STEP_M:
            raise GenericAdapterValidationError(
                "drivable-only reconstruction is ambiguous or disconnected; provide progression_supports or global_plan_supports"
            )
        tangent = _blend_tangent(step_vector, future_anchor, next_midpoint)
        current_center = next_midpoint

    if len(reconstructed) < 2:
        raise GenericAdapterValidationError(
            "drivable-only reconstruction could not build a usable centerline; provide progression_supports or global_plan_supports"
        )
    return tuple(reconstructed)


def load_generic_snapshot(input_path: str | Path) -> tuple[SemanticInputSnapshot, QueryContext]:
    """Load a generic local semantic map fixture into the canonical contract."""

    path = Path(input_path)
    payload = _load_payload(path)
    _reject_removed_key(
        payload,
        "branch_supports",
        message="branch_supports is no longer supported; express split/merge as multiple progression_supports",
    )

    metadata = dict(payload.get("metadata", {}))
    drivable_regions = _polygon_list(_require_sequence(payload, "drivable_regions"), key="drivable_regions")
    progression_guides_raw = _optional_sequence(payload, "progression_supports")
    global_plan_guides_raw = _optional_sequence(payload, "global_plan_supports")
    boundaries = _polyline_list(_optional_sequence(payload, "boundaries"), key="boundaries")
    boundary_regions = _polygon_list(_optional_sequence(payload, "boundary_regions"), key="boundary_regions")
    safety_regions = _polygon_list(_optional_sequence(payload, "safety_regions"), key="safety_regions")
    rule_regions = _polygon_list(_optional_sequence(payload, "rule_regions"), key="rule_regions")
    dynamic_regions = _polygon_list(_optional_sequence(payload, "dynamic_regions"), key="dynamic_regions")

    progression_options = _optional_mapping(payload, "progression_options")

    query_context = _require_mapping(payload, "query_context")
    pose_raw = query_context.get("query_pose", query_context.get("ego_pose"))
    if not isinstance(pose_raw, dict):
        raise GenericAdapterValidationError("query_context must contain query_pose or ego_pose")
    local_window = _require_mapping(query_context, "local_window")

    future_anchor_raw = progression_options.get("future_anchor")
    future_anchor = (
        _coerce_point(future_anchor_raw, path="progression_options.future_anchor")
        if future_anchor_raw is not None
        else None
    )
    ego_pose = StateSample(
        x=_require_float(pose_raw, "x", path="query_context.query_pose"),
        y=_require_float(pose_raw, "y", path="query_context.query_pose"),
        yaw=_require_float(pose_raw, "yaw", path="query_context.query_pose"),
    )

    if progression_guides_raw:
        progression_guides = _polyline_list(progression_guides_raw, key="progression_supports")
    elif global_plan_guides_raw:
        progression_guides = _polyline_list(global_plan_guides_raw, key="global_plan_supports")
    else:
        reconstructed_points = _reconstruct_centerline_from_drivable(
            drivable_regions,
            ego_pose=ego_pose,
            future_anchor=future_anchor,
        )
        progression_guides = (
            DirectedPolyline(
                guide_id="reconstructed_progression",
                points=reconstructed_points,
                weight=1.0,
                metadata={"source": "drivable_only_reconstruction"},
            ),
        )

    snapshot = SemanticInputSnapshot(
        metadata=metadata,
        drivable_support=DrivableSupport(regions=drivable_regions),
        progression_support=ProgressionSupport(
            guides=progression_guides,
            reverse_context=bool(progression_options.get("reverse_context", False)),
            future_anchor=future_anchor,
            phase=str(progression_options["phase"]) if progression_options.get("phase") is not None else None,
        ),
        boundary_interior_support=BoundaryInteriorSupport(
            boundaries=boundaries,
            boundary_regions=boundary_regions,
        ),
        exception_layer_support=ExceptionLayerSupport(
            safety_regions=safety_regions,
            rule_regions=rule_regions,
            dynamic_regions=dynamic_regions,
        ),
    )
    context = QueryContext(
        semantic_snapshot=snapshot,
        ego_pose=ego_pose,
        local_window=QueryWindow(
            x_min=_require_float(local_window, "x_min", path="query_context.local_window"),
            x_max=_require_float(local_window, "x_max", path="query_context.local_window"),
            y_min=_require_float(local_window, "y_min", path="query_context.local_window"),
            y_max=_require_float(local_window, "y_max", path="query_context.local_window"),
        ),
        mode=str(query_context["mode"]) if query_context.get("mode") is not None else None,
        phase=str(query_context["phase"]) if query_context.get("phase") is not None else None,
    )
    return snapshot, context


def serialize_snapshot(snapshot: SemanticInputSnapshot) -> dict[str, Any]:
    def serialize_region(region: PolygonRegion) -> dict[str, Any]:
        return {
            "region_id": region.region_id,
            "points": [list(point) for point in region.points],
            "severity": region.severity,
            "hard": region.hard,
            "influence_radius": region.influence_radius,
            "metadata": dict(region.metadata),
        }

    def serialize_guide(guide: DirectedPolyline) -> dict[str, Any]:
        return {
            "guide_id": guide.guide_id,
            "points": [list(point) for point in guide.points],
            "weight": guide.weight,
            "metadata": dict(guide.metadata),
        }

    return {
        "metadata": dict(snapshot.metadata),
        "drivable_support": {
            "regions": [serialize_region(region) for region in snapshot.drivable_support.regions],
        },
        "progression_support": {
            "guides": [serialize_guide(guide) for guide in snapshot.progression_support.guides],
            "reverse_context": snapshot.progression_support.reverse_context,
            "future_anchor": list(snapshot.progression_support.future_anchor)
            if snapshot.progression_support.future_anchor is not None
            else None,
            "phase": snapshot.progression_support.phase,
        },
        "boundary_interior_support": {
            "boundaries": [serialize_guide(guide) for guide in snapshot.boundary_interior_support.boundaries],
            "boundary_regions": [
                serialize_region(region) for region in snapshot.boundary_interior_support.boundary_regions
            ],
        },
        "exception_layer_support": {
            "safety_regions": [serialize_region(region) for region in snapshot.exception_layer_support.safety_regions],
            "rule_regions": [serialize_region(region) for region in snapshot.exception_layer_support.rule_regions],
            "dynamic_regions": [
                serialize_region(region) for region in snapshot.exception_layer_support.dynamic_regions
            ],
        },
    }


def serialize_query_context(context: QueryContext) -> dict[str, Any]:
    return {
        "ego_pose": {
            "x": context.ego_pose.x,
            "y": context.ego_pose.y,
            "yaw": context.ego_pose.yaw,
        },
        "local_window": {
            "x_min": context.local_window.x_min,
            "x_max": context.local_window.x_max,
            "y_min": context.local_window.y_min,
            "y_max": context.local_window.y_max,
        },
        "mode": context.mode,
        "phase": context.phase,
    }


def serialize_canonical_bundle(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    include_summary: bool = True,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "snapshot": serialize_snapshot(snapshot),
        "query_context": serialize_query_context(context),
    }
    if include_summary:
        payload["summary"] = summarize_snapshot(snapshot)
    return payload
