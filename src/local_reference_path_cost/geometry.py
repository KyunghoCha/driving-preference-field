from __future__ import annotations

import math

from .contracts import DirectedPolyline, Point2, PolygonRegion, StateSample

EPS = 1e-9


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def point_in_polygon(point: Point2, polygon: tuple[Point2, ...]) -> bool:
    x, y = point
    inside = False
    n = len(polygon)
    if n < 3:
        return False
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / ((y2 - y1) + EPS) + x1
        )
        if intersects:
            inside = not inside
    return inside


def distance_point_to_segment(point: Point2, start: Point2, end: Point2) -> float:
    px, py = point
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    denom = dx * dx + dy * dy
    if denom <= EPS:
        return math.hypot(px - sx, py - sy)
    t = clamp(((px - sx) * dx + (py - sy) * dy) / denom, 0.0, 1.0)
    cx = sx + t * dx
    cy = sy + t * dy
    return math.hypot(px - cx, py - cy)


def distance_point_to_polyline(point: Point2, polyline: tuple[Point2, ...]) -> float:
    if len(polyline) < 2:
        return math.inf
    return min(
        distance_point_to_segment(point, polyline[i], polyline[i + 1])
        for i in range(len(polyline) - 1)
    )


def distance_point_to_polygon_boundary(point: Point2, polygon: tuple[Point2, ...]) -> float:
    if len(polygon) < 2:
        return math.inf
    return min(
        distance_point_to_segment(point, polygon[i], polygon[(i + 1) % len(polygon)])
        for i in range(len(polygon))
    )


def signed_distance_to_polygon(point: Point2, polygon: tuple[Point2, ...]) -> float:
    boundary = distance_point_to_polygon_boundary(point, polygon)
    return boundary if point_in_polygon(point, polygon) else -boundary


def polyline_length(polyline: tuple[Point2, ...]) -> float:
    if len(polyline) < 2:
        return 0.0
    return sum(
        math.hypot(polyline[i + 1][0] - polyline[i][0], polyline[i + 1][1] - polyline[i][1])
        for i in range(len(polyline) - 1)
    )


def heading_unit(yaw: float) -> Point2:
    return (math.cos(yaw), math.sin(yaw))


def dot(a: Point2, b: Point2) -> float:
    return a[0] * b[0] + a[1] * b[1]


def normalize(v: Point2) -> Point2:
    norm = math.hypot(v[0], v[1])
    if norm <= EPS:
        return (0.0, 0.0)
    return (v[0] / norm, v[1] / norm)


def nearest_projection_on_polyline(point: Point2, guide: DirectedPolyline) -> dict[str, float | Point2]:
    points = guide.points
    if len(points) < 2:
        return {
            "distance": math.inf,
            "progress": 0.0,
            "tangent": (0.0, 0.0),
            "projected_point": point,
            "guide_length": 0.0,
        }

    best_distance = math.inf
    best_progress = 0.0
    best_tangent = (0.0, 0.0)
    best_point = points[0]
    accumulated = 0.0
    total_length = polyline_length(points)

    for i in range(len(points) - 1):
        start = points[i]
        end = points[i + 1]
        seg = (end[0] - start[0], end[1] - start[1])
        seg_len_sq = seg[0] * seg[0] + seg[1] * seg[1]
        seg_len = math.sqrt(seg_len_sq)
        if seg_len_sq <= EPS:
            continue
        t = clamp(
            ((point[0] - start[0]) * seg[0] + (point[1] - start[1]) * seg[1]) / seg_len_sq,
            0.0,
            1.0,
        )
        projected = (start[0] + t * seg[0], start[1] + t * seg[1])
        distance = math.hypot(point[0] - projected[0], point[1] - projected[1])
        if distance < best_distance:
            best_distance = distance
            best_progress = accumulated + t * seg_len
            best_tangent = normalize(seg)
            best_point = projected
        accumulated += seg_len

    return {
        "distance": best_distance,
        "progress": best_progress,
        "tangent": best_tangent,
        "projected_point": best_point,
        "guide_length": total_length,
    }


def state_from_point_and_yaw(x: float, y: float, yaw: float) -> StateSample:
    return StateSample(x=x, y=y, yaw=yaw)


def nearest_polygon_signed_distance(point: Point2, regions: tuple[PolygonRegion, ...]) -> float:
    if not regions:
        return -math.inf
    return max(signed_distance_to_polygon(point, region.points) for region in regions)
