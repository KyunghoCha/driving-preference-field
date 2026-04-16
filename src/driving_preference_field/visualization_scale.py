from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


SCALE_MODE_FIXED = "fixed"
SCALE_MODE_NORMALIZED = "normalized"


@dataclass(frozen=True)
class ChannelScaleSpec:
    unit: str
    fixed_min: float
    fixed_max: float
    diff_abs_max: float


CHANNEL_SCALE_SPECS = {
    "progression_tilted": ChannelScaleSpec(
        unit="score",
        fixed_min=0.0,
        fixed_max=5.0,
        diff_abs_max=5.0,
    ),
    "progression_s_hat": ChannelScaleSpec(
        unit="m",
        fixed_min=-2.0,
        fixed_max=10.0,
        diff_abs_max=4.0,
    ),
    "progression_n_hat": ChannelScaleSpec(
        unit="m",
        fixed_min=0.0,
        fixed_max=4.0,
        diff_abs_max=2.0,
    ),
    "progression_longitudinal_component": ChannelScaleSpec(
        unit="score",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=1.0,
    ),
    "progression_transverse_component": ChannelScaleSpec(
        unit="score",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=1.0,
    ),
    "progression_support_mod": ChannelScaleSpec(
        unit="score",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=0.1,
    ),
    "progression_alignment_mod": ChannelScaleSpec(
        unit="score",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=0.1,
    ),
    "safety_soft": ChannelScaleSpec(
        unit="burden score",
        fixed_min=0.0,
        fixed_max=2.0,
        diff_abs_max=2.0,
    ),
    "rule_soft": ChannelScaleSpec(
        unit="burden score",
        fixed_min=0.0,
        fixed_max=2.0,
        diff_abs_max=2.0,
    ),
    "dynamic_soft": ChannelScaleSpec(
        unit="burden score",
        fixed_min=0.0,
        fixed_max=2.0,
        diff_abs_max=2.0,
    ),
    "hard_unsafe_mask": ChannelScaleSpec(
        unit="binary",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=1.0,
    ),
    "hard_rule_mask": ChannelScaleSpec(
        unit="binary",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=1.0,
    ),
    "hard_dynamic_mask": ChannelScaleSpec(
        unit="binary",
        fixed_min=0.0,
        fixed_max=1.0,
        diff_abs_max=1.0,
    ),
}


def scale_spec_for(channel_name: str) -> ChannelScaleSpec:
    return CHANNEL_SCALE_SPECS[channel_name]


def resolve_display_range(
    data: np.ndarray,
    *,
    channel_name: str,
    scale_mode: str,
    diff: bool = False,
) -> tuple[float, float]:
    spec = scale_spec_for(channel_name)
    if scale_mode == SCALE_MODE_FIXED:
        if diff:
            return (-spec.diff_abs_max, spec.diff_abs_max)
        return (spec.fixed_min, spec.fixed_max)
    if diff:
        max_abs = max(float(np.max(np.abs(data))), 1e-9)
        return (-max_abs, max_abs)
    data_min = float(np.min(data))
    data_max = float(np.max(data))
    if math.isclose(data_min, data_max):
        return (data_min, data_max + 1e-9)
    return (data_min, data_max)


def display_unit(channel_name: str, *, diff: bool = False) -> str:
    spec = scale_spec_for(channel_name)
    return "binary delta" if diff and spec.unit == "binary" else ("score delta" if diff else spec.unit)


def format_display_range(
    channel_name: str,
    *,
    scale_mode: str,
    value_range: tuple[float, float],
    diff: bool = False,
) -> str:
    unit = display_unit(channel_name, diff=diff)
    vmin, vmax = value_range
    mode_label = "fixed" if scale_mode == SCALE_MODE_FIXED else "normalized"
    return f"{mode_label} | range=[{vmin:.3f}, {vmax:.3f}] | unit={unit}"
