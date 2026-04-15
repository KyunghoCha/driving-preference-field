from __future__ import annotations

"""Base field channels used by the tiny evaluator.

The project-level formulas are documented in README.md and
docs/reference/current_formula_reference_ko.md. This module keeps
the three current base channels separate so base preference totals remain easy
to inspect and compare.
"""

import math
from typing import Any

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample
from .geometry import (
    clamp,
    distance_point_to_polygon_boundary,
    distance_point_to_polyline,
    dot,
    heading_unit,
    nearest_projection_on_polyline,
    point_in_polygon,
    signed_distance_to_polygon,
)
from .progression_surface import progression_surface_details


def progression_tilted_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> dict[str, Any]:
    field_config = config or DEFAULT_FIELD_CONFIG
    return progression_surface_details(
        snapshot,
        context,
        state,
        config=field_config.progression,
    )


def progression_tilted(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> float:
    return float(progression_tilted_details(snapshot, context, state, config=config)["score"])


def interior_signed_margin(
    snapshot: SemanticInputSnapshot,
    state: StateSample,
) -> float:
    point = state.point
    drivable_regions = snapshot.drivable_support.regions
    if not drivable_regions:
        return -math.inf

    best_signed_distance = -math.inf
    for region in drivable_regions:
        signed_distance = signed_distance_to_polygon(point, region.points)
        best_signed_distance = max(best_signed_distance, signed_distance)

    if best_signed_distance <= 0.0:
        return best_signed_distance

    explicit_boundaries = snapshot.boundary_interior_support.boundaries
    if explicit_boundaries:
        return min(distance_point_to_polyline(point, boundary.points) for boundary in explicit_boundaries)
    return best_signed_distance


def interior_boundary(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> float:
    del context
    field_config = config or DEFAULT_FIELD_CONFIG
    interior_config = field_config.interior_boundary
    drivable_regions = snapshot.drivable_support.regions
    if not drivable_regions:
        return 0.0

    point = state.point
    best_margin_score = 0.0
    for region in drivable_regions:
        if point_in_polygon(point, region.points):
            boundary_distance = distance_point_to_polygon_boundary(point, region.points)
            margin_scale = float(region.metadata.get("margin_scale", 1.5)) * interior_config.margin_scale_multiplier
            margin_score = interior_config.gain * clamp(boundary_distance / max(margin_scale, 1e-6), 0.0, 1.0)
            best_margin_score = max(best_margin_score, margin_score)
    return best_margin_score


def continuity_branch_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> dict[str, Any]:
    del context
    field_config = config or DEFAULT_FIELD_CONFIG
    branch_config = field_config.continuity_branch
    guides = snapshot.branch_continuity_support.guides
    if not guides:
        return {
            "score": 0.0,
            "guide_id": None,
            "distance": math.inf,
            "alignment": 0.0,
        }

    best = {
        "score": 0.0,
        "guide_id": None,
        "distance": math.inf,
        "alignment": 0.0,
    }
    heading = heading_unit(state.yaw)
    for guide in guides:
        projection = nearest_projection_on_polyline(state.point, guide)
        tangent = projection["tangent"]
        distance = float(projection["distance"])
        alignment = max(0.0, dot(heading, tangent)) * branch_config.alignment_weight
        proximity = math.exp(-distance / max(branch_config.distance_scale, 1e-6))
        confidence = float(guide.metadata.get("confidence", 1.0))
        score = (
            branch_config.gain
            * guide.weight
            * min(confidence, branch_config.confidence_ceiling)
            * proximity
            * alignment
        )
        if score > float(best["score"]):
            best = {
                "score": score,
                "guide_id": guide.guide_id,
                "distance": distance,
                "alignment": alignment,
            }
    return best


def continuity_branch(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> float:
    return float(continuity_branch_details(snapshot, context, state, config=config)["score"])
