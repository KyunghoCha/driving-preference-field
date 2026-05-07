from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from local_reference_path_cost.ui.colormaps import colormap_stops


class ColorScaleWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._cmap_name = "viridis"
        self._value_range = (0.0, 1.0)
        self._diff = False
        self.setMinimumWidth(56)
        self.setMaximumWidth(72)

    def set_scale(self, *, cmap_name: str, value_range: tuple[float, float], diff: bool) -> None:
        self._cmap_name = cmap_name
        self._value_range = value_range
        self._diff = diff
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        bar_width = 14
        top_margin = 12
        bottom_margin = 12
        bar_height = max(height - top_margin - bottom_margin, 24)
        bar_x = 6
        bar_y = top_margin

        gradient = QLinearGradient(bar_x, bar_y + bar_height, bar_x, bar_y)
        for t, rgba in colormap_stops(self._cmap_name):
            r, g, b, a = rgba
            gradient.setColorAt(t, QColor.fromRgbF(r, g, b, a))

        rect = QRectF(bar_x, bar_y, bar_width, bar_height)
        painter.fillRect(rect, gradient)
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawRect(rect)

        label_x = bar_x + bar_width + 6
        range_min, range_max = self._value_range
        midpoint = 0.0 if self._diff else (range_min + range_max) * 0.5
        painter.setPen(QColor("#222222"))
        painter.drawText(label_x, bar_y + 4, width - label_x - 2, 14, Qt.AlignmentFlag.AlignLeft, f"{range_max:.2f}")
        painter.drawText(
            label_x,
            bar_y + (bar_height // 2) - 7,
            width - label_x - 2,
            14,
            Qt.AlignmentFlag.AlignLeft,
            f"{midpoint:.2f}",
        )
        painter.drawText(
            label_x,
            bar_y + bar_height - 10,
            width - label_x - 2,
            14,
            Qt.AlignmentFlag.AlignLeft,
            f"{range_min:.2f}",
        )
