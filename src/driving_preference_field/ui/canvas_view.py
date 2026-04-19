from __future__ import annotations

import math

import numpy as np
from PyQt6.QtCore import QPoint, QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap, QTransform
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsView,
)

from driving_preference_field.contracts import DirectedPolyline, QueryWindow, SemanticInputSnapshot, StateSample
from driving_preference_field.ui.colormaps import sample_colormap


LAYER_KEYS = (
    "progression_guides",
    "progression_targets",
    "drivable_boundary",
    "ego",
    "hard_masks",
)


class RasterCanvasView(QGraphicsView):
    hoverChanged = pyqtSignal(float, float)

    def __init__(self) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._window: QueryWindow | None = None
        self._content_rect = None
        self._overlay_visibility = {key: True for key in LAYER_KEYS}
        self._snapshot: SemanticInputSnapshot | None = None
        self._context_ego: StateSample | None = None
        self.scale(1.0, -1.0)

    def set_overlay_visibility(self, visibility: dict[str, bool]) -> None:
        self._overlay_visibility.update(visibility)
        self._redraw_overlays()

    def set_scene_content(
        self,
        image: QImage,
        *,
        window: QueryWindow,
        snapshot: SemanticInputSnapshot,
        ego_pose: StateSample,
    ) -> None:
        self._scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(image))
        width = window.x_max - window.x_min
        height = window.y_max - window.y_min
        self._pixmap_item.setPos(window.x_min, window.y_min)
        self._pixmap_item.setTransform(QTransform().scale(width / image.width(), height / image.height()))
        self._scene.addItem(self._pixmap_item)
        self._window = window
        self._content_rect = (window.x_min, window.y_min, width, height)
        self._snapshot = snapshot
        self._context_ego = ego_pose
        self._redraw_overlays()
        pan_margin = max(width, height) * 0.5
        self.setSceneRect(
            window.x_min - pan_margin,
            window.y_min - pan_margin,
            width + 2.0 * pan_margin,
            height + 2.0 * pan_margin,
        )

    def reset_view(self) -> None:
        if self._content_rect is None:
            return
        x, y, width, height = self._content_rect
        left_pad = 0.08 * width
        right_pad = 0.02 * width
        bottom_pad = 0.10 * height
        top_pad = 0.02 * height
        self.fitInView(
            x - left_pad,
            y - bottom_pad,
            width + left_pad + right_pad,
            height + bottom_pad + top_pad,
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def wheelEvent(self, event) -> None:
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(factor, factor)

    def mouseMoveEvent(self, event) -> None:
        point = self.mapToScene(event.position().toPoint())
        self.hoverChanged.emit(point.x(), point.y())
        super().mouseMoveEvent(event)

    def _redraw_overlays(self) -> None:
        if self._snapshot is None or self._context_ego is None:
            return
        for item in list(self._scene.items()):
            if item is self._pixmap_item:
                continue
            self._scene.removeItem(item)
        if self._overlay_visibility.get("hard_masks", True):
            self._draw_hard_mask_bounds()
        if self._overlay_visibility.get("progression_guides", True):
            for guide in self._snapshot.progression_support.guides:
                self._draw_polyline(guide, color=QColor("cyan"))
        if self._overlay_visibility.get("progression_targets", True):
            self._draw_progression_targets()
        if self._overlay_visibility.get("drivable_boundary", True):
            for region in self._snapshot.drivable_support.regions:
                closed = DirectedPolyline(
                    guide_id=f"{region.region_id}_boundary",
                    points=tuple(region.points) + (region.points[0],),
                )
                self._draw_polyline(closed, color=QColor("white"))
        if self._overlay_visibility.get("ego", True):
            self._draw_ego_pose(self._context_ego)

    def _draw_polyline(self, guide: DirectedPolyline, *, color: QColor, dashed: bool = False) -> None:
        pen = QPen(color, 0.04)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        for start, end in zip(guide.points, guide.points[1:]):
            item = QGraphicsLineItem(start[0], start[1], end[0], end[1])
            item.setPen(pen)
            self._scene.addItem(item)

    def _draw_ego_pose(self, ego_pose: StateSample) -> None:
        radius = 0.12
        points = [
            QPointF(0.24, 0.0),
            QPointF(-0.18, 0.10),
            QPointF(-0.18, -0.10),
        ]
        polygon = QGraphicsPolygonItem()
        polygon.setPolygon(matplotlib_to_qpolygon(points))
        polygon.setBrush(QColor("white"))
        polygon.setPen(QPen(QColor("white"), 0.03))
        polygon.setPos(ego_pose.x, ego_pose.y)
        polygon.setRotation(math.degrees(ego_pose.yaw))
        self._scene.addItem(polygon)

    def _draw_hard_mask_bounds(self) -> None:
        support = self._snapshot.exception_layer_support
        for region in support.safety_regions:
            if not region.hard:
                continue
            self._draw_region_outline(region.points, QColor("red"))
        for region in support.rule_regions:
            if not region.hard:
                continue
            self._draw_region_outline(region.points, QColor("orange"))
        for region in support.dynamic_regions:
            if not region.hard:
                continue
            self._draw_region_outline(region.points, QColor("magenta"))

    def _draw_region_outline(self, points: tuple[tuple[float, float], ...], color: QColor) -> None:
        closed = DirectedPolyline(guide_id="mask", points=tuple(points) + (points[0],))
        self._draw_polyline(closed, color=color)

    def _draw_progression_targets(self) -> None:
        future_anchor = self._snapshot.progression_support.future_anchor
        for guide in self._snapshot.progression_support.guides:
            self._draw_endpoint_marker(
                guide.points[-1],
                color=QColor("#ffd400"),
                closed_loop=bool(guide.points[0] == guide.points[-1]),
            )
        if future_anchor is not None:
            self._draw_future_anchor_marker(future_anchor)

    def _draw_endpoint_marker(self, point: tuple[float, float], *, color: QColor, closed_loop: bool) -> None:
        radius = 0.14 if closed_loop else 0.10
        item = QGraphicsEllipseItem(point[0] - radius, point[1] - radius, 2.0 * radius, 2.0 * radius)
        item.setBrush(color)
        item.setPen(QPen(QColor("black"), 0.03))
        self._scene.addItem(item)
        if not closed_loop:
            return
        inner_radius = 0.07
        ring = QGraphicsEllipseItem(
            point[0] - inner_radius,
            point[1] - inner_radius,
            2.0 * inner_radius,
            2.0 * inner_radius,
        )
        ring.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        ring.setPen(QPen(QColor("black"), 0.025))
        self._scene.addItem(ring)

    def _draw_future_anchor_marker(self, point: tuple[float, float]) -> None:
        radius = 0.16
        item = QGraphicsEllipseItem(point[0] - radius, point[1] - radius, 2.0 * radius, 2.0 * radius)
        item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        item.setPen(QPen(QColor("#ff4fd8"), 0.03))
        self._scene.addItem(item)
        for dx0, dy0, dx1, dy1 in (
            (-0.12, 0.0, 0.12, 0.0),
            (0.0, -0.12, 0.0, 0.12),
        ):
            cross = QGraphicsLineItem(point[0] + dx0, point[1] + dy0, point[0] + dx1, point[1] + dy1)
            cross.setPen(QPen(QColor("#ff4fd8"), 0.03))
            self._scene.addItem(cross)

    def drawForeground(self, painter: QPainter, rect) -> None:  # noqa: N802
        super().drawForeground(painter, rect)
        if self._content_rect is None:
            return

        x, y, width, height = self._content_rect
        bottom_left = self.mapFromScene(QPointF(x, y))
        top_right = self.mapFromScene(QPointF(x + width, y + height))

        left = min(bottom_left.x(), top_right.x())
        right = max(bottom_left.x(), top_right.x())
        top = min(bottom_left.y(), top_right.y())
        bottom = max(bottom_left.y(), top_right.y())
        mid_x = 0.5 * (left + right)
        mid_y = 0.5 * (top + bottom)

        painter.save()
        painter.resetTransform()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        axis_pen = QPen(QColor("#64748b"), 1.2)
        tick_pen = QPen(QColor("#64748b"), 1.0)
        text_pen = QPen(QColor("#334155"), 1.0)
        tick_len = 7
        label_gap = 4

        painter.setPen(axis_pen)
        painter.drawLine(left, bottom, right, bottom)
        painter.drawLine(left, top, left, bottom)

        painter.setPen(tick_pen)
        for tick_x in (left, mid_x, right):
            painter.drawLine(int(tick_x), int(bottom), int(tick_x), int(bottom + tick_len))
        for tick_y in (bottom, mid_y, top):
            painter.drawLine(int(left - tick_len), int(tick_y), int(left), int(tick_y))

        painter.setPen(text_pen)
        self._draw_axis_label(painter, f"{x:.1f}", left, bottom + tick_len + label_gap, align="center_top")
        self._draw_axis_label(painter, f"{x + 0.5 * width:.1f}", mid_x, bottom + tick_len + label_gap, align="center_top")
        self._draw_axis_label(painter, f"{x + width:.1f}", right, bottom + tick_len + label_gap, align="center_top")

        self._draw_axis_label(painter, f"{y:.1f}", left - tick_len - label_gap, bottom, align="right_middle")
        self._draw_axis_label(painter, f"{y + 0.5 * height:.1f}", left - tick_len - label_gap, mid_y, align="right_middle")
        self._draw_axis_label(painter, f"{y + height:.1f}", left - tick_len - label_gap, top, align="right_middle")

        painter.restore()

    def _draw_axis_label(self, painter: QPainter, text: str, x: float, y: float, *, align: str) -> None:
        metrics = painter.fontMetrics()
        width = metrics.horizontalAdvance(text)
        height = metrics.height()
        x_pos = x
        y_pos = y
        if align == "center_top":
            x_pos -= 0.5 * width
            y_pos += height
        elif align == "right_middle":
            x_pos -= width
            y_pos += 0.35 * height
        painter.drawText(QPointF(x_pos, y_pos), text)


def raster_to_qimage(
    data: np.ndarray,
    *,
    cmap_name: str,
    symmetric: bool = False,
    value_range: tuple[float, float] | None = None,
) -> QImage:
    working = np.asarray(data, dtype=float)
    if working.size == 0:
        raise ValueError("empty raster")
    if value_range is not None:
        range_min, range_max = value_range
        if math.isclose(range_min, range_max):
            normalized = np.zeros_like(working, dtype=float)
        else:
            normalized = (working - range_min) / (range_max - range_min)
    elif symmetric:
        max_abs = max(float(np.max(np.abs(working))), 1e-9)
        normalized = (working + max_abs) / (2.0 * max_abs)
    else:
        data_min = float(np.min(working))
        data_max = float(np.max(working))
        if math.isclose(data_min, data_max):
            normalized = np.zeros_like(working, dtype=float)
        else:
            normalized = (working - data_min) / (data_max - data_min)
    normalized = np.clip(normalized, 0.0, 1.0)
    rgba = sample_colormap(cmap_name, normalized, bytes=True)
    image = QImage(
        rgba.data,
        rgba.shape[1],
        rgba.shape[0],
        rgba.strides[0],
        QImage.Format.Format_RGBA8888,
    )
    return image.copy()


def matplotlib_to_qpolygon(points: list[QPointF]) -> "QPolygonF":
    from PyQt6.QtGui import QPolygonF

    return QPolygonF(points)
