from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import (
    BoundaryInteriorSupport,
    BranchContinuitySupport,
    DirectedPolyline,
    DrivableSupport,
    ExceptionLayerSupport,
    PolygonRegion,
    ProgressionSupport,
    QueryContext,
    QueryWindow,
    SemanticInputSnapshot,
    StateSample,
)


def _point_list(raw_points: list[list[float]]) -> tuple[tuple[float, float], ...]:
    return tuple((float(x), float(y)) for x, y in raw_points)


def _polygon_list(items: list[dict]) -> tuple[PolygonRegion, ...]:
    regions: list[PolygonRegion] = []
    for idx, item in enumerate(items):
        regions.append(
            PolygonRegion(
                region_id=str(item.get("id", f"region_{idx}")),
                points=_point_list(item["points"]),
                severity=float(item.get("severity", 1.0)),
                hard=bool(item.get("hard", False)),
                influence_radius=float(item.get("influence_radius", 1.0)),
                metadata=dict(item.get("metadata", {})),
            )
        )
    return tuple(regions)


def _polyline_list(items: list[dict]) -> tuple[DirectedPolyline, ...]:
    guides: list[DirectedPolyline] = []
    for idx, item in enumerate(items):
        guides.append(
            DirectedPolyline(
                guide_id=str(item.get("id", f"guide_{idx}")),
                points=_point_list(item["points"]),
                weight=float(item.get("weight", 1.0)),
                metadata=dict(item.get("metadata", {})),
            )
        )
    return tuple(guides)


def load_toy_snapshot(case_path: str | Path) -> tuple[SemanticInputSnapshot, QueryContext]:
    """Load a prototype toy case into the canonical semantic contract.

    The toy YAML schema is a hand-authored prototype input case. It is not the
    canonical design contract of the project; it only fills the semantic slots
    needed by the tiny analytic evaluator skeleton.
    """

    path = Path(case_path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    metadata = dict(payload.get("metadata", {}))
    drivable_regions = _polygon_list(payload.get("drivable_regions", []))
    progression_guides = _polyline_list(payload.get("progression_guides", []))
    boundary_regions = _polygon_list(payload.get("boundary_regions", []))
    boundaries = _polyline_list(payload.get("boundaries", []))
    branch_guides = _polyline_list(payload.get("branch_guides", []))
    safety_regions = _polygon_list(payload.get("safety_regions", []))
    rule_regions = _polygon_list(payload.get("rule_regions", []))
    dynamic_regions = _polygon_list(payload.get("dynamic_regions", []))

    snapshot = SemanticInputSnapshot(
        metadata=metadata,
        drivable_support=DrivableSupport(regions=drivable_regions),
        progression_support=ProgressionSupport(
            guides=progression_guides,
            reverse_context=bool(payload.get("reverse_context", False)),
            future_anchor=tuple(payload["future_anchor"]) if payload.get("future_anchor") else None,
            phase=payload.get("phase"),
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

    window_data = payload["query_window"]
    ego_data = payload["ego_pose"]
    context = QueryContext(
        semantic_snapshot=snapshot,
        ego_pose=StateSample(
            x=float(ego_data["x"]),
            y=float(ego_data["y"]),
            yaw=float(ego_data["yaw"]),
        ),
        local_window=QueryWindow(
            x_min=float(window_data["x_min"]),
            x_max=float(window_data["x_max"]),
            y_min=float(window_data["y_min"]),
            y_max=float(window_data["y_max"]),
        ),
        mode=payload.get("mode"),
        phase=payload.get("phase"),
    )
    return snapshot, context


def summarize_snapshot(snapshot: SemanticInputSnapshot) -> dict[str, object]:
    return {
        "metadata": snapshot.metadata,
        "drivable_regions": len(snapshot.drivable_support.regions),
        "progression_guides": len(snapshot.progression_support.guides),
        "boundaries": len(snapshot.boundary_interior_support.boundaries),
        "boundary_regions": len(snapshot.boundary_interior_support.boundary_regions),
        "branch_guides": len(snapshot.branch_continuity_support.guides),
        "safety_regions": len(snapshot.exception_layer_support.safety_regions),
        "rule_regions": len(snapshot.exception_layer_support.rule_regions),
        "dynamic_regions": len(snapshot.exception_layer_support.dynamic_regions),
    }
