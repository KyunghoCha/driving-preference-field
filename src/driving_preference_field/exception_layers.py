from __future__ import annotations

"""Soft and hard exception-layer burdens.

Soft exception channels are summed as spatial burdens. Hard exception channels
stay boolean and are handled ahead of base preference in trajectory ordering.
"""

import math

from .contracts import PolygonRegion, QueryContext, SemanticInputSnapshot, StateSample
from .geometry import point_in_polygon, signed_distance_to_polygon


def _soft_region_burden(point: tuple[float, float], region: PolygonRegion) -> float:
    signed_distance = signed_distance_to_polygon(point, region.points)
    if signed_distance >= 0.0:
        return region.severity
    influence = max(region.influence_radius, 1e-6)
    return region.severity * math.exp(signed_distance / influence)


def _hard_region_hit(point: tuple[float, float], region: PolygonRegion) -> bool:
    return region.hard and point_in_polygon(point, region.points)


def evaluate_exception_layers(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
) -> tuple[dict[str, float], dict[str, bool]]:
    del context
    point = state.point
    support = snapshot.exception_layer_support

    safety_soft = sum(_soft_region_burden(point, region) for region in support.safety_regions)
    rule_soft = sum(_soft_region_burden(point, region) for region in support.rule_regions)
    dynamic_soft = sum(_soft_region_burden(point, region) for region in support.dynamic_regions)

    hard_flags = {
        "unsafe": any(_hard_region_hit(point, region) for region in support.safety_regions),
        "rule_blocked": any(_hard_region_hit(point, region) for region in support.rule_regions),
        "dynamic_blocked": any(_hard_region_hit(point, region) for region in support.dynamic_regions),
    }
    soft_channels = {
        "safety_soft": safety_soft,
        "rule_soft": rule_soft,
        "dynamic_soft": dynamic_soft,
    }
    return soft_channels, hard_flags
