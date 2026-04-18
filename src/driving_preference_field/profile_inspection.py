from __future__ import annotations

"""Line-profile inspection helpers for morphology debugging.

These helpers operate on rasterized field samples. They are part of the SSOT
research tooling rather than the canonical field definition.
"""

from io import BytesIO
import json
from pathlib import Path
from typing import Any

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .profile_contracts import ComparisonProfileResult, ProfileSlice, ProfileSpec
from .raster import RasterSampleResult

DEFAULT_PROFILE_CHANNELS = (
    "progression_tilted",
    "progression_s_hat",
    "progression_center_distance",
    "progression_longitudinal_component",
    "progression_transverse_term",
)

def _interpolate_profile(
    data: np.ndarray,
    *,
    axis: int,
    coords: np.ndarray,
    coordinate: float,
) -> tuple[np.ndarray, float]:
    if coords.size == 0:
        return np.zeros((0,), dtype=float), float(coordinate)
    if coords.size == 1:
        if axis == 0:
            return np.asarray(data[0], dtype=float), float(coords[0])
        return np.asarray(data[:, 0], dtype=float), float(coords[0])

    clipped = float(np.clip(coordinate, float(coords[0]), float(coords[-1])))
    insert_index = int(np.searchsorted(coords, clipped))
    if insert_index <= 0:
        if axis == 0:
            return np.asarray(data[0], dtype=float), clipped
        return np.asarray(data[:, 0], dtype=float), clipped
    if insert_index >= coords.size:
        if axis == 0:
            return np.asarray(data[-1], dtype=float), clipped
        return np.asarray(data[:, -1], dtype=float), clipped

    lower = insert_index - 1
    upper = insert_index
    span = float(coords[upper] - coords[lower])
    ratio = 0.0 if span <= 1e-9 else (clipped - float(coords[lower])) / span
    if axis == 0:
        return (1.0 - ratio) * np.asarray(data[lower], dtype=float) + ratio * np.asarray(data[upper], dtype=float), clipped
    return (1.0 - ratio) * np.asarray(data[:, lower], dtype=float) + ratio * np.asarray(data[:, upper], dtype=float), clipped


def _channel_names(selected_channel: str, extra_channels: tuple[str, ...] = DEFAULT_PROFILE_CHANNELS) -> tuple[str, ...]:
    names = [selected_channel]
    for channel_name in extra_channels:
        if channel_name not in names:
            names.append(channel_name)
    return tuple(names)


def extract_raster_profile(
    raster: RasterSampleResult,
    *,
    spec: ProfileSpec,
    channel_names: tuple[str, ...],
) -> ProfileSlice:
    if spec.axis not in {"horizontal", "vertical"}:
        raise ValueError("profile axis must be 'horizontal' or 'vertical'")
    if spec.axis == "horizontal":
        positions = np.asarray(raster.x_coords, dtype=float)
        slices = {
            channel_name: _interpolate_profile(
                np.asarray(raster.channels[channel_name], dtype=float),
                axis=0,
                coords=np.asarray(raster.y_coords, dtype=float),
                coordinate=spec.coordinate,
            )[0]
            for channel_name in channel_names
        }
        _, clamped_coordinate = _interpolate_profile(
            np.asarray(raster.channels[channel_names[0]], dtype=float),
            axis=0,
            coords=np.asarray(raster.y_coords, dtype=float),
            coordinate=spec.coordinate,
        )
    else:
        positions = np.asarray(raster.y_coords, dtype=float)
        slices = {
            channel_name: _interpolate_profile(
                np.asarray(raster.channels[channel_name], dtype=float),
                axis=1,
                coords=np.asarray(raster.x_coords, dtype=float),
                coordinate=spec.coordinate,
            )[0]
            for channel_name in channel_names
        }
        _, clamped_coordinate = _interpolate_profile(
            np.asarray(raster.channels[channel_names[0]], dtype=float),
            axis=1,
            coords=np.asarray(raster.x_coords, dtype=float),
            coordinate=spec.coordinate,
        )
    return ProfileSlice(
        spec=ProfileSpec(axis=spec.axis, coordinate=clamped_coordinate),
        positions=positions,
        channels=slices,
    )


def build_comparison_profile(
    baseline_raster: RasterSampleResult,
    candidate_raster: RasterSampleResult,
    *,
    spec: ProfileSpec,
    selected_channel: str,
) -> ComparisonProfileResult:
    channel_names = _channel_names(selected_channel)
    baseline = extract_raster_profile(baseline_raster, spec=spec, channel_names=channel_names)
    candidate = extract_raster_profile(candidate_raster, spec=spec, channel_names=channel_names)
    diff = ProfileSlice(
        spec=candidate.spec,
        positions=np.asarray(candidate.positions, dtype=float),
        channels={
            channel_name: np.asarray(candidate.channels[channel_name], dtype=float)
            - np.asarray(baseline.channels[channel_name], dtype=float)
            for channel_name in channel_names
        },
    )
    return ComparisonProfileResult(
        spec=candidate.spec,
        baseline=baseline,
        candidate=candidate,
        diff=diff,
    )


def summarize_profile_result(
    result: ComparisonProfileResult,
    *,
    selected_channel: str,
) -> dict[str, object]:
    return {
        "spec": result.spec.to_dict(),
        "selected_channel": selected_channel,
        "baseline_selected_range": _series_range(result.baseline.channels[selected_channel]),
        "candidate_selected_range": _series_range(result.candidate.channels[selected_channel]),
        "diff_selected_range": _series_range(result.diff.channels[selected_channel]),
    }


def _series_range(values: np.ndarray) -> dict[str, float]:
    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
    }


def _plot_profile_axes(
    axes,
    profile: ProfileSlice,
    *,
    selected_channel: str,
    title: str,
    diff: bool,
) -> None:
    x_values = profile.positions
    line_desc = f"{profile.spec.axis} {profile.spec.coordinate_axis}={profile.spec.coordinate:.3f}"
    axes[0].plot(x_values, profile.channels[selected_channel], color="#2a6fdb", linewidth=2.0)
    if diff:
        axes[0].axhline(0.0, color="#666666", linewidth=0.8, linestyle="--")
    axes[0].set_ylabel(selected_channel)
    axes[0].set_title(f"{title} | {line_desc}")
    axes[0].grid(alpha=0.25)

    axes[1].plot(x_values, profile.channels["progression_s_hat"], label="s_hat", color="#1b9e77", linewidth=1.6)
    axes[1].plot(
        x_values,
        profile.channels["progression_center_distance"],
        label="center_distance",
        color="#d95f02",
        linewidth=1.6,
    )
    if diff:
        axes[1].axhline(0.0, color="#666666", linewidth=0.8, linestyle="--")
    axes[1].set_ylabel("coords")
    axes[1].grid(alpha=0.25)
    axes[1].legend(loc="best", fontsize=8)

    axes[2].plot(
        x_values,
        profile.channels["progression_longitudinal_component"],
        label="longitudinal",
        color="#7570b3",
        linewidth=1.6,
    )
    axes[2].plot(
        x_values,
        profile.channels["progression_transverse_term"],
        label="transverse_term",
        color="#e7298a",
        linewidth=1.6,
    )
    if diff:
        axes[2].axhline(0.0, color="#666666", linewidth=0.8, linestyle="--")
    axes[2].set_ylabel("components")
    axes[2].set_xlabel(profile.spec.sample_axis)
    axes[2].grid(alpha=0.25)
    axes[2].legend(loc="best", fontsize=8)


def profile_plot_png_bytes(
    result: ComparisonProfileResult,
    *,
    selected_channel: str,
    view: str,
    dpi: int = 140,
) -> bytes:
    profile = {
        "baseline": result.baseline,
        "candidate": result.candidate,
        "diff": result.diff,
    }[view]
    figure = Figure(figsize=(7.4, 6.4), dpi=dpi)
    axes = figure.subplots(3, 1, sharex=True)
    _plot_profile_axes(
        axes,
        profile,
        selected_channel=selected_channel,
        title=view.capitalize(),
        diff=view == "diff",
    )
    figure.tight_layout()
    buffer = BytesIO()
    FigureCanvasAgg(figure).print_png(buffer)
    return buffer.getvalue()


def export_profile_bundle(
    result: ComparisonProfileResult,
    *,
    selected_channel: str,
    out_dir: Path,
    prefix: str = "profile",
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    file_manifest: dict[str, str] = {}
    for view in ("baseline", "candidate", "diff"):
        path = out_dir / f"{prefix}_{view}.png"
        path.write_bytes(profile_plot_png_bytes(result, selected_channel=selected_channel, view=view))
        file_manifest[path.name] = str(path)

    payload = {
        "available": True,
        "selected_channel": selected_channel,
        "summary": summarize_profile_result(result, selected_channel=selected_channel),
        "result": result.to_dict(),
        "file_manifest": file_manifest,
    }
    data_path = out_dir / f"{prefix}_data.json"
    data_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    file_manifest[data_path.name] = str(data_path)
    payload["file_manifest"] = file_manifest
    data_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
