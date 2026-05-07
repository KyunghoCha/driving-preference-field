from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Point2 = tuple[float, float]


@dataclass(frozen=True)
class PolygonRegion:
    """Prototype polygon region for toy cases and exception layers."""

    region_id: str
    points: tuple[Point2, ...]
    severity: float = 1.0
    hard: bool = False
    influence_radius: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DirectedPolyline:
    """Directed polyline used for progression, boundary, or overlay geometry."""

    guide_id: str
    points: tuple[Point2, ...]
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DrivableSupport:
    regions: tuple[PolygonRegion, ...]


@dataclass(frozen=True)
class ProgressionSupport:
    guides: tuple[DirectedPolyline, ...]
    reverse_context: bool = False
    future_anchor: Point2 | None = None
    phase: str | None = None


@dataclass(frozen=True)
class BoundaryInteriorSupport:
    boundaries: tuple[DirectedPolyline, ...] = ()
    boundary_regions: tuple[PolygonRegion, ...] = ()


@dataclass(frozen=True)
class ExceptionLayerSupport:
    safety_regions: tuple[PolygonRegion, ...] = ()
    rule_regions: tuple[PolygonRegion, ...] = ()
    dynamic_regions: tuple[PolygonRegion, ...] = ()


@dataclass(frozen=True)
class SemanticInputSnapshot:
    metadata: dict[str, Any]
    drivable_support: DrivableSupport
    progression_support: ProgressionSupport
    boundary_interior_support: BoundaryInteriorSupport
    exception_layer_support: ExceptionLayerSupport


@dataclass(frozen=True)
class QueryWindow:
    x_min: float
    x_max: float
    y_min: float
    y_max: float


@dataclass(frozen=True)
class StateSample:
    x: float
    y: float
    yaw: float

    @property
    def point(self) -> Point2:
        return (self.x, self.y)


@dataclass(frozen=True)
class TrajectorySample:
    states: tuple[StateSample, ...]


@dataclass(frozen=True)
class QueryContext:
    semantic_snapshot: SemanticInputSnapshot
    ego_pose: StateSample
    local_window: QueryWindow
    mode: str | None = None
    phase: str | None = None
