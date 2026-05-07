from __future__ import annotations

from functools import lru_cache

import numpy as np


def _hex_rgba(value: str) -> tuple[float, float, float, float]:
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"expected #RRGGBB hex color, got {value!r}")
    return tuple(int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4)) + (1.0,)


_COLORMAP_HEX_STOPS = {
    "viridis": (
        "#440154",
        "#482878",
        "#3e4989",
        "#31688e",
        "#26828e",
        "#1f9e89",
        "#35b779",
        "#6dcd59",
        "#b4de2c",
        "#fde725",
    ),
    "plasma": (
        "#0d0887",
        "#46039f",
        "#7201a8",
        "#9c179e",
        "#bd3786",
        "#d8576b",
        "#ed7953",
        "#fb9f3a",
        "#fdca26",
        "#f0f921",
    ),
    "magma": (
        "#000004",
        "#180f3d",
        "#440f76",
        "#721f81",
        "#9e2f7f",
        "#cd4071",
        "#f1605d",
        "#fd9668",
        "#feca8d",
        "#fcfdbf",
    ),
    "inferno": (
        "#000004",
        "#1b0c41",
        "#4a0c6b",
        "#781c6d",
        "#a52c60",
        "#cf4446",
        "#ed6925",
        "#fb9b06",
        "#f7d13d",
        "#fcffa4",
    ),
    "cividis": (
        "#00224e",
        "#123570",
        "#3b496c",
        "#575d6d",
        "#707173",
        "#8a8678",
        "#a59c74",
        "#c3b369",
        "#e1cc55",
        "#fee838",
    ),
    "coolwarm": (
        "#3b4cc0",
        "#6282ea",
        "#8db0fe",
        "#b9d0f9",
        "#dddcdc",
        "#f2cbb7",
        "#f6a283",
        "#df634e",
        "#b40426",
    ),
}


@lru_cache(maxsize=None)
def colormap_stops(name: str) -> tuple[tuple[float, tuple[float, float, float, float]], ...]:
    try:
        hex_stops = _COLORMAP_HEX_STOPS[name]
    except KeyError as exc:
        raise KeyError(f"unknown colormap: {name}") from exc
    if len(hex_stops) == 1:
        return ((0.0, _hex_rgba(hex_stops[0])),)
    return tuple(
        (index / (len(hex_stops) - 1), _hex_rgba(hex_value))
        for index, hex_value in enumerate(hex_stops)
    )


def sample_colormap(name: str, values, *, bytes: bool = False) -> np.ndarray:
    stops = colormap_stops(name)
    positions = np.asarray([position for position, _ in stops], dtype=float)
    rgba = np.asarray([color for _, color in stops], dtype=float)
    normalized = np.clip(np.asarray(values, dtype=float), 0.0, 1.0)
    channels = [
        np.interp(normalized, positions, rgba[:, channel_index])
        for channel_index in range(4)
    ]
    stacked = np.stack(channels, axis=-1)
    if bytes:
        return np.rint(stacked * 255.0).astype(np.uint8)
    return stacked
