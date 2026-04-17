from __future__ import annotations

from PyQt6.QtCore import Qt


CHANNEL_OPTIONS = {
    "progression_tilted": "plasma",
    "progression_s_hat": "viridis",
    "progression_n_hat": "magma",
    "progression_longitudinal_component": "plasma",
    "progression_transverse_component": "cividis",
    "progression_support_mod": "inferno",
    "progression_alignment_mod": "inferno",
    "safety_soft": "inferno",
    "rule_soft": "magma",
    "dynamic_soft": "cividis",
}


COMPARE_LAYOUT_OPTIONS = {
    "stacked": Qt.Orientation.Vertical,
    "side_by_side": Qt.Orientation.Horizontal,
}
