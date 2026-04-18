from __future__ import annotations

import math
from dataclasses import dataclass

from .config import DEFAULT_FIELD_CONFIG
from .contracts import DirectedPolyline
from .geometry import dot, nearest_projection_on_polyline, normalize

_DEFAULT_ANCHOR_SPACING_M = DEFAULT_FIELD_CONFIG.surface_tuning.anchor_spacing_m
_MIN_ENDPOINT_GAP_TOLERANCE_M = 0.20
_ANCHOR_SPACING_GAP_SCALE = 0.75
_HEADING_CONTINUITY_TOLERANCE_DEG = 35.0
_OVERLAP_PREFIX_RATIO = 0.60
_OVERLAP_SUFFIX_RATIO = 0.40
_NEAR_THRESHOLD_RATIO = 0.80
_COLLINEAR_DISTANCE_TOLERANCE_M = 0.02
_COLLINEAR_HEADING_TOLERANCE_DEG = 5.0
_EPS = 1e-9


@dataclass(frozen=True)
class ProgressionNormalizationResult:
    guides: tuple[DirectedPolyline, ...]
    metadata_block: dict[str, object] | None


@dataclass(frozen=True)
class _GuideShape:
    guide: DirectedPolyline
    start_tangent: tuple[float, float]
    end_tangent: tuple[float, float]
    length: float
    original_index: int


@dataclass(frozen=True)
class _EdgeMetrics:
    gap_to_next: float
    gap_to_prev: float
    heading_deg: float


def normalize_progression_guides(
    guides: tuple[DirectedPolyline, ...],
    *,
    source_kind: str,
    anchor_spacing_m: float = _DEFAULT_ANCHOR_SPACING_M,
) -> ProgressionNormalizationResult:
    if len(guides) <= 1:
        return ProgressionNormalizationResult(guides=guides, metadata_block=None)

    gap_tolerance_m = max(_MIN_ENDPOINT_GAP_TOLERANCE_M, _ANCHOR_SPACING_GAP_SCALE * anchor_spacing_m)
    heading_cos_tolerance = math.cos(math.radians(_HEADING_CONTINUITY_TOLERANCE_DEG))
    shapes = tuple(
        _GuideShape(
            guide=guide,
            start_tangent=_endpoint_tangent(guide.points, from_start=True),
            end_tangent=_endpoint_tangent(guide.points, from_start=False),
            length=_polyline_length(guide.points),
            original_index=index,
        )
        for index, guide in enumerate(guides)
    )
    edges, edge_metrics = _candidate_edges(shapes, gap_tolerance_m=gap_tolerance_m, heading_cos_tolerance=heading_cos_tolerance)
    components = _weak_components(shapes, edges)

    output_guides: list[tuple[int, DirectedPolyline]] = []
    merged_groups: list[list[str]] = []
    messages: list[str] = []
    applied = False
    saw_ambiguous = False
    saw_near_threshold = False

    for component in components:
        if len(component) == 1:
            shape = shapes[component[0]]
            output_guides.append((shape.original_index, shape.guide))
            continue
        component_nodes = set(component)
        component_edges = {node: [target for target in edges[node] if target in component_nodes] for node in component}
        indegree = {node: 0 for node in component}
        edge_count = 0
        for node in component:
            for target in component_edges[node]:
                indegree[target] += 1
                edge_count += 1
        if not _is_clean_chain(component, component_edges, indegree, edge_count):
            saw_ambiguous = True
            messages.append(
                f"{source_kind} fragmented guides stayed unmerged because continuation was ambiguous: "
                + ", ".join(shapes[node].guide.guide_id for node in sorted(component, key=lambda n: shapes[n].original_index))
            )
            for node in sorted(component, key=lambda n: shapes[n].original_index):
                shape = shapes[node]
                output_guides.append((shape.original_index, shape.guide))
            continue
        ordered_nodes = _ordered_chain(component, component_edges, indegree)
        chain_shapes = [shapes[node] for node in ordered_nodes]
        merged_groups.append([shape.guide.guide_id for shape in chain_shapes])
        merged_guide = _merge_chain(chain_shapes, source_kind=source_kind, gap_tolerance_m=gap_tolerance_m)
        output_guides.append((min(shape.original_index for shape in chain_shapes), merged_guide))
        applied = True
        if _chain_is_near_threshold(ordered_nodes, edge_metrics, gap_tolerance_m=gap_tolerance_m):
            saw_near_threshold = True
            messages.append(
                f"{source_kind} fragmented guide chain was merged near the gap/heading threshold: {merged_guide.guide_id}"
            )

    output_guides.sort(key=lambda item: item[0])
    normalized_guides = tuple(guide for _, guide in output_guides)
    if not applied and not saw_ambiguous:
        return ProgressionNormalizationResult(guides=normalized_guides, metadata_block=None)

    severity = "info"
    if saw_ambiguous:
        severity = "error"
    elif source_kind in {"progression_supports", "toy_case"} or saw_near_threshold:
        severity = "warning"
    if applied and source_kind in {"progression_supports", "toy_case"}:
        messages.insert(
            0,
            f"{source_kind} explicit progression input was fragmented; best-effort normalization merged {len(merged_groups)} chain(s).",
        )
    elif applied:
        messages.insert(
            0,
            f"{source_kind} fragmented progression input was cleanly normalized into canonical guide chain(s).",
        )
    metadata_block = {
        "source_kind": source_kind,
        "applied": applied,
        "severity": severity,
        "input_guide_count": len(guides),
        "output_guide_count": len(normalized_guides),
        "merged_groups": merged_groups,
        "messages": messages,
    }
    return ProgressionNormalizationResult(guides=normalized_guides, metadata_block=metadata_block)


def _endpoint_tangent(points: tuple[tuple[float, float], ...], *, from_start: bool) -> tuple[float, float]:
    if from_start:
        pairs = zip(points[:-1], points[1:])
    else:
        pairs = ((points[index - 1], points[index]) for index in range(len(points) - 1, 0, -1))
    for a, b in pairs:
        vector = (b[0] - a[0], b[1] - a[1])
        tangent = normalize(vector)
        if abs(tangent[0]) > _EPS or abs(tangent[1]) > _EPS:
            return tangent
    return (0.0, 0.0)


def _polyline_length(points: tuple[tuple[float, float], ...]) -> float:
    return sum(math.hypot(points[index + 1][0] - points[index][0], points[index + 1][1] - points[index][1]) for index in range(len(points) - 1))


def _candidate_edges(
    shapes: tuple[_GuideShape, ...],
    *,
    gap_tolerance_m: float,
    heading_cos_tolerance: float,
) -> tuple[dict[int, list[int]], dict[tuple[int, int], _EdgeMetrics]]:
    edges: dict[int, list[int]] = {index: [] for index in range(len(shapes))}
    metrics: dict[tuple[int, int], _EdgeMetrics] = {}
    for source in shapes:
        for target in shapes:
            if source.original_index == target.original_index:
                continue
            if dot(source.end_tangent, target.start_tangent) < heading_cos_tolerance:
                continue
            projection_on_target = nearest_projection_on_polyline(source.guide.points[-1], target.guide)
            projection_on_source = nearest_projection_on_polyline(target.guide.points[0], source.guide)
            if projection_on_target["distance"] > gap_tolerance_m or projection_on_source["distance"] > gap_tolerance_m:
                continue
            if projection_on_target["progress"] > _OVERLAP_PREFIX_RATIO * target.length:
                continue
            if projection_on_source["progress"] < _OVERLAP_SUFFIX_RATIO * source.length:
                continue
            forward_extension = dot(
                (
                    target.guide.points[-1][0] - source.guide.points[-1][0],
                    target.guide.points[-1][1] - source.guide.points[-1][1],
                ),
                source.end_tangent,
            )
            if forward_extension <= gap_tolerance_m:
                continue
            edges[source.original_index].append(target.original_index)
            metrics[(source.original_index, target.original_index)] = _EdgeMetrics(
                gap_to_next=float(projection_on_target["distance"]),
                gap_to_prev=float(projection_on_source["distance"]),
                heading_deg=_heading_angle_deg(source.end_tangent, target.start_tangent),
            )
    return edges, metrics


def _weak_components(shapes: tuple[_GuideShape, ...], edges: dict[int, list[int]]) -> list[list[int]]:
    undirected: dict[int, set[int]] = {shape.original_index: set() for shape in shapes}
    for source, targets in edges.items():
        for target in targets:
            undirected[source].add(target)
            undirected[target].add(source)
    remaining = set(undirected)
    components: list[list[int]] = []
    while remaining:
        root = min(remaining)
        stack = [root]
        component: list[int] = []
        remaining.remove(root)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in undirected[node]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def _is_clean_chain(component: list[int], edges: dict[int, list[int]], indegree: dict[int, int], edge_count: int) -> bool:
    starts = [node for node in component if indegree[node] == 0]
    ends = [node for node in component if len(edges[node]) == 0]
    if len(starts) != 1 or len(ends) != 1:
        return False
    if edge_count != len(component) - 1:
        return False
    return all(indegree[node] <= 1 and len(edges[node]) <= 1 for node in component)


def _ordered_chain(component: list[int], edges: dict[int, list[int]], indegree: dict[int, int]) -> list[int]:
    current = next(node for node in component if indegree[node] == 0)
    ordered = [current]
    seen = {current}
    while edges[current]:
        current = edges[current][0]
        if current in seen:
            break
        ordered.append(current)
        seen.add(current)
    return ordered


def _chain_is_near_threshold(
    ordered_nodes: list[int],
    edge_metrics: dict[tuple[int, int], _EdgeMetrics],
    *,
    gap_tolerance_m: float,
) -> bool:
    heading_threshold = _HEADING_CONTINUITY_TOLERANCE_DEG * _NEAR_THRESHOLD_RATIO
    gap_threshold = gap_tolerance_m * _NEAR_THRESHOLD_RATIO
    for source, target in zip(ordered_nodes[:-1], ordered_nodes[1:]):
        metrics = edge_metrics[(source, target)]
        if (
            metrics.gap_to_next >= gap_threshold
            or metrics.gap_to_prev >= gap_threshold
            or metrics.heading_deg >= heading_threshold
        ):
            return True
    return False


def _merge_chain(
    chain: list[_GuideShape],
    *,
    source_kind: str,
    gap_tolerance_m: float,
) -> DirectedPolyline:
    merged_points = list(chain[0].guide.points)
    for shape in chain[1:]:
        merged_points = _append_guide_points(merged_points, shape.guide.points, gap_tolerance_m=gap_tolerance_m)
    merged_points = _drop_redundant_collinear_points(tuple(merged_points))
    weights = [shape.guide.weight for shape in chain]
    confidences = [float(shape.guide.metadata.get("support_confidence", 1.0)) for shape in chain]
    metadata = dict(chain[0].guide.metadata)
    metadata["normalized_from"] = [shape.guide.guide_id for shape in chain]
    metadata["normalization_source_kind"] = source_kind
    metadata["support_confidence"] = sum(confidences) / max(len(confidences), 1)
    guide_id = f"{chain[0].guide.guide_id}__normalized_chain"
    return DirectedPolyline(
        guide_id=guide_id,
        points=merged_points,
        weight=sum(weights) / max(len(weights), 1),
        metadata=metadata,
    )


def _append_guide_points(
    base_points: list[tuple[float, float]],
    next_points: tuple[tuple[float, float], ...],
    *,
    gap_tolerance_m: float,
) -> list[tuple[float, float]]:
    current_end = base_points[-1]
    next_guide = DirectedPolyline(guide_id="_next", points=next_points)
    projection = nearest_projection_on_polyline(current_end, next_guide)
    if projection["distance"] > gap_tolerance_m:
        if _distance(base_points[-1], next_points[0]) <= gap_tolerance_m:
            return [*base_points, *next_points[1:]]
        return [*base_points, *next_points]

    accumulated = 0.0
    start_index = len(next_points) - 1
    for index in range(len(next_points) - 1):
        a = next_points[index]
        b = next_points[index + 1]
        segment_length = math.hypot(b[0] - a[0], b[1] - a[1])
        if accumulated + segment_length + _EPS >= projection["progress"]:
            start_index = index + 1
            break
        accumulated += segment_length
    appended = list(base_points)
    for point in next_points[start_index:]:
        if _distance(appended[-1], point) > _EPS:
            appended.append(point)
    return appended


def _drop_redundant_collinear_points(points: tuple[tuple[float, float], ...]) -> tuple[tuple[float, float], ...]:
    if len(points) <= 2:
        return points
    result = [points[0]]
    cos_tol = math.cos(math.radians(_COLLINEAR_HEADING_TOLERANCE_DEG))
    for index in range(1, len(points) - 1):
        previous = result[-1]
        current = points[index]
        nxt = points[index + 1]
        first = normalize((current[0] - previous[0], current[1] - previous[1]))
        second = normalize((nxt[0] - current[0], nxt[1] - current[1]))
        if dot(first, second) >= cos_tol and _distance_to_segment(current, previous, nxt) <= _COLLINEAR_DISTANCE_TOLERANCE_M:
            continue
        result.append(current)
    result.append(points[-1])
    return tuple(result)


def _distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def _distance_to_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    denom = dx * dx + dy * dy
    if denom <= _EPS:
        return _distance(point, start)
    t = max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / denom))
    projected = (start[0] + t * dx, start[1] + t * dy)
    return _distance(point, projected)


def _heading_angle_deg(a: tuple[float, float], b: tuple[float, float]) -> float:
    if abs(a[0]) <= _EPS and abs(a[1]) <= _EPS:
        return 180.0
    if abs(b[0]) <= _EPS and abs(b[1]) <= _EPS:
        return 180.0
    cosine = max(-1.0, min(1.0, dot(a, b)))
    return math.degrees(math.acos(cosine))
