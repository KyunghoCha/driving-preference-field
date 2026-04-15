from __future__ import annotations

"""Generic source adapter for canonical semantic snapshot generation.

This module defines a reference adapter that reads a generic local semantic map
fixture and translates it into the canonical SemanticInputSnapshot +
QueryContext contract. The input shape stays source-agnostic on purpose: it is
a generic external-like schema rather than a downstream-specific wire format.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from .contracts import (
    BoundaryInteriorSupport,
    BranchContinuitySupport,
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
    for key in ("support_confidence", "branch_prior"):
        if key in item and key not in metadata:
            try:
                metadata[key] = float(item[key])
            except (TypeError, ValueError) as exc:
                raise GenericAdapterValidationError(f"{path}.{key} must be numeric") from exc
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


def load_generic_snapshot(input_path: str | Path) -> tuple[SemanticInputSnapshot, QueryContext]:
    """Load a generic local semantic map fixture into the canonical contract."""

    path = Path(input_path)
    payload = _load_payload(path)

    metadata = dict(payload.get("metadata", {}))
    drivable_regions = _polygon_list(_require_sequence(payload, "drivable_regions"), key="drivable_regions")
    progression_guides = _polyline_list(
        _require_sequence(payload, "progression_supports"),
        key="progression_supports",
    )
    boundaries = _polyline_list(_optional_sequence(payload, "boundaries"), key="boundaries")
    boundary_regions = _polygon_list(_optional_sequence(payload, "boundary_regions"), key="boundary_regions")
    branch_guides = _polyline_list(_optional_sequence(payload, "branch_supports"), key="branch_supports")
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
        branch_continuity_support=BranchContinuitySupport(guides=branch_guides),
        exception_layer_support=ExceptionLayerSupport(
            safety_regions=safety_regions,
            rule_regions=rule_regions,
            dynamic_regions=dynamic_regions,
        ),
    )
    context = QueryContext(
        semantic_snapshot=snapshot,
        ego_pose=StateSample(
            x=_require_float(pose_raw, "x", path="query_context.query_pose"),
            y=_require_float(pose_raw, "y", path="query_context.query_pose"),
            yaw=_require_float(pose_raw, "yaw", path="query_context.query_pose"),
        ),
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
        "branch_continuity_support": {
            "guides": [serialize_guide(guide) for guide in snapshot.branch_continuity_support.guides],
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
