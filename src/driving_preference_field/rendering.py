from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import DirectedPolyline, QueryContext, SemanticInputSnapshot
from .raster import RasterSampleResult, sample_local_raster
from .visualization_scale import SCALE_MODE_FIXED, display_unit, format_display_range, resolve_display_range

CHANNEL_DESCRIPTIONS = {
    "progression_tilted": "Whole-fabric blended progression space over the local map. Higher means stronger progression ordering.",
    "interior_boundary": "Interior preference derived from boundary margin. Higher means deeper interior support.",
    "continuity_branch": "Continuation preference near split/merge structure. Higher means more coherent continuation.",
    "base_preference_total": "Sum of the three base preference channels.",
    "safety_soft": "Distance-based safety burden from safety regions. Higher means stronger obstacle/safety burden.",
    "rule_soft": "Soft burden from rule-related regions.",
    "dynamic_soft": "Soft burden from dynamic interaction regions.",
    "hard_unsafe_mask": "Binary mask for hard unsafe states.",
    "hard_rule_mask": "Binary mask for hard rule-blocked states.",
    "hard_dynamic_mask": "Binary mask for hard dynamic-blocked states.",
}

CHANNEL_TITLES = {
    "progression_tilted": "Progression Tilted",
    "interior_boundary": "Interior Boundary",
    "continuity_branch": "Continuity Branch",
    "base_preference_total": "Base Preference Total",
    "safety_soft": "Safety Soft Burden",
    "hard_unsafe_mask": "Hard Unsafe Mask",
    "hard_rule_mask": "Hard Rule Mask",
    "hard_dynamic_mask": "Hard Dynamic Mask",
}


@dataclass(frozen=True)
class RenderArtifacts:
    out_dir: Path
    file_manifest: dict[str, str]
    summary: dict[str, object]


def _render_heatmap(
    path: Path,
    data: np.ndarray,
    extent: tuple[float, float, float, float],
    *,
    channel_name: str,
    title: str,
    cmap: str,
    dpi: int,
    scale_mode: str,
) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 5.8), dpi=dpi)
    value_range = resolve_display_range(data, channel_name=channel_name, scale_mode=scale_mode)
    image = ax.imshow(
        data,
        origin="lower",
        extent=extent,
        cmap=cmap,
        vmin=value_range[0],
        vmax=value_range[1],
        aspect="auto",
    )
    fig.colorbar(image, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.subplots_adjust(left=0.10, right=0.92, top=0.90, bottom=0.20)
    fig.text(
        0.10,
        0.06,
        textwrap.fill(CHANNEL_DESCRIPTIONS[channel_name], width=72),
        va="bottom",
        ha="left",
        color="black",
        fontsize=9,
        bbox={"facecolor": "#f4f4f4", "alpha": 0.95, "edgecolor": "#cccccc", "pad": 4},
    )
    fig.text(
        0.90,
        0.03,
        format_display_range(channel_name, scale_mode=scale_mode, value_range=value_range),
        va="bottom",
        ha="right",
        color="#333333",
        fontsize=8,
    )
    fig.savefig(path)
    plt.close(fig)


def _render_mask(
    path: Path,
    data: np.ndarray,
    extent: tuple[float, float, float, float],
    *,
    channel_name: str,
    title: str,
    color: str,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 5.8), dpi=dpi)
    mask = np.ma.masked_where(data.astype(bool) == 0, data.astype(int))
    ax.imshow(np.zeros_like(data, dtype=float), origin="lower", extent=extent, cmap="gray", vmin=0.0, vmax=1.0, aspect="auto")
    ax.imshow(mask, origin="lower", extent=extent, cmap=matplotlib.colors.ListedColormap([color]), vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.subplots_adjust(left=0.10, right=0.92, top=0.90, bottom=0.20)
    fig.text(
        0.10,
        0.06,
        textwrap.fill(CHANNEL_DESCRIPTIONS[channel_name], width=72),
        va="bottom",
        ha="left",
        color="black",
        fontsize=9,
        bbox={"facecolor": "#f4f4f4", "alpha": 0.95, "edgecolor": "#cccccc", "pad": 4},
    )
    fig.savefig(path)
    plt.close(fig)


def _plot_polyline(ax: plt.Axes, guide: DirectedPolyline, *, color: str, linestyle: str = "-", linewidth: float = 1.5) -> None:
    xs = [point[0] for point in guide.points]
    ys = [point[1] for point in guide.points]
    ax.plot(xs, ys, color=color, linestyle=linestyle, linewidth=linewidth)


def _render_composite(
    path: Path,
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    raster: RasterSampleResult,
    extent: tuple[float, float, float, float],
    *,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(6.8, 5.8), dpi=dpi)
    base_image = ax.imshow(
        raster.channels["base_preference_total"],
        origin="lower",
        extent=extent,
        cmap="viridis",
        aspect="auto",
    )
    fig.colorbar(base_image, ax=ax, fraction=0.046, pad=0.03)

    ax.imshow(
        np.ma.masked_where(~raster.channels["hard_unsafe_mask"], raster.channels["hard_unsafe_mask"].astype(int)),
        origin="lower",
        extent=extent,
        cmap=matplotlib.colors.ListedColormap(["red"]),
        alpha=0.5,
        aspect="auto",
    )
    ax.imshow(
        np.ma.masked_where(~raster.channels["hard_rule_mask"], raster.channels["hard_rule_mask"].astype(int)),
        origin="lower",
        extent=extent,
        cmap=matplotlib.colors.ListedColormap(["orange"]),
        alpha=0.35,
        aspect="auto",
    )
    ax.imshow(
        np.ma.masked_where(~raster.channels["hard_dynamic_mask"], raster.channels["hard_dynamic_mask"].astype(int)),
        origin="lower",
        extent=extent,
        cmap=matplotlib.colors.ListedColormap(["magenta"]),
        alpha=0.35,
        aspect="auto",
    )

    for guide in snapshot.progression_support.guides:
        _plot_polyline(ax, guide, color="cyan", linestyle="-", linewidth=1.5)
    for guide in snapshot.branch_continuity_support.guides:
        _plot_polyline(ax, guide, color="yellow", linestyle="--", linewidth=1.2)
    for region in snapshot.drivable_support.regions:
        boundary = DirectedPolyline(
            guide_id=f"{region.region_id}_boundary",
            points=tuple(region.points) + (region.points[0],),
        )
        _plot_polyline(ax, boundary, color="white", linestyle="-", linewidth=1.0)

    ego = context.ego_pose
    dx = 0.35 * np.cos(ego.yaw)
    dy = 0.35 * np.sin(ego.yaw)
    ax.scatter([ego.x], [ego.y], color="white", s=28, marker="^")
    ax.arrow(ego.x, ego.y, dx, dy, color="white", width=0.02, head_width=0.12, length_includes_head=True)
    ax.set_title("Composite Debug View")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.subplots_adjust(left=0.10, right=0.90, top=0.90, bottom=0.12)
    fig.text(
        0.10,
        0.03,
        "Overlay legend is exported separately in render_legend.png.",
        va="bottom",
        ha="left",
        color="#333333",
        fontsize=8,
    )
    fig.savefig(path)
    plt.close(fig)


def _render_legend(path: Path, *, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=dpi)
    ax.axis("off")
    lines = ["Render Legend", ""]
    for channel_name in (
        "progression_tilted",
        "interior_boundary",
        "continuity_branch",
        "base_preference_total",
        "safety_soft",
    ):
        lines.extend(
            textwrap.wrap(
                f"{CHANNEL_TITLES[channel_name]}: {CHANNEL_DESCRIPTIONS[channel_name]}",
                width=78,
                subsequent_indent="  ",
            )
        )
    lines.extend(
        [
            "",
            "Hard masks: binary hard-violation regions for safety, rule, and dynamic layers",
            "",
            "Composite overlay:",
            "  red = hard unsafe, orange = hard rule, magenta = hard dynamic",
            "  cyan = progression guide, yellow dashed = branch guide",
            "  white = drivable boundary and ego pose",
        ]
    )
    text = "\n".join(lines)
    ax.text(0.02, 0.98, text, va="top", ha="left", fontsize=11, family="monospace")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _channel_min_max(data: np.ndarray) -> dict[str, float]:
    return {"min": float(np.min(data)), "max": float(np.max(data))}


def summarize_diff_array(data: np.ndarray) -> dict[str, float]:
    return {
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "mean": float(np.mean(data)),
    }


def render_case(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    case_name: str,
    config: FieldConfig | None = None,
    out_dir: str | Path | None = None,
    x_samples: int = 160,
    y_samples: int = 160,
    dpi: int = 160,
    scale_mode: str = SCALE_MODE_FIXED,
) -> RenderArtifacts:
    field_config = config or DEFAULT_FIELD_CONFIG
    raster = sample_local_raster(snapshot, context, config=field_config, x_samples=x_samples, y_samples=y_samples)
    base_out_dir = Path(out_dir) if out_dir is not None else Path("artifacts/render") / case_name
    base_out_dir.mkdir(parents=True, exist_ok=True)

    extent = (
        context.local_window.x_min,
        context.local_window.x_max,
        context.local_window.y_min,
        context.local_window.y_max,
    )
    file_manifest: dict[str, str] = {}

    outputs = {
        "progression_tilted.png": ("progression_tilted", CHANNEL_TITLES["progression_tilted"], "plasma"),
        "interior_boundary.png": ("interior_boundary", CHANNEL_TITLES["interior_boundary"], "magma"),
        "continuity_branch.png": ("continuity_branch", CHANNEL_TITLES["continuity_branch"], "cividis"),
        "base_total.png": ("base_preference_total", CHANNEL_TITLES["base_preference_total"], "viridis"),
        "safety_soft.png": ("safety_soft", CHANNEL_TITLES["safety_soft"], "inferno"),
    }
    for filename, (channel_name, title, cmap) in outputs.items():
        path = base_out_dir / filename
        _render_heatmap(
            path,
            raster.channels[channel_name],
            extent,
            channel_name=channel_name,
            title=title,
            cmap=cmap,
            dpi=dpi,
            scale_mode=scale_mode,
        )
        file_manifest[filename] = str(path)

    masks = {
        "hard_unsafe_mask.png": ("hard_unsafe_mask", CHANNEL_TITLES["hard_unsafe_mask"], "red"),
        "hard_rule_mask.png": ("hard_rule_mask", CHANNEL_TITLES["hard_rule_mask"], "orange"),
        "hard_dynamic_mask.png": ("hard_dynamic_mask", CHANNEL_TITLES["hard_dynamic_mask"], "magenta"),
    }
    for filename, (channel_name, title, color) in masks.items():
        path = base_out_dir / filename
        _render_mask(
            path,
            raster.channels[channel_name],
            extent,
            channel_name=channel_name,
            title=title,
            color=color,
            dpi=dpi,
        )
        file_manifest[filename] = str(path)

    composite_path = base_out_dir / "composite_debug.png"
    _render_composite(composite_path, snapshot, context, raster, extent, dpi=dpi)
    file_manifest["composite_debug.png"] = str(composite_path)

    legend_path = base_out_dir / "render_legend.png"
    _render_legend(legend_path, dpi=dpi)
    file_manifest["render_legend.png"] = str(legend_path)

    summary = {
        "case_name": case_name,
        "query_window": raster.metadata["query_window"],
        "raster_resolution": {"x_samples": x_samples, "y_samples": y_samples},
        "field_config": field_config.to_dict(),
        "visualization_scale_mode": scale_mode,
        "channel_ranges": {
            "progression_tilted": _channel_min_max(raster.channels["progression_tilted"]),
            "interior_boundary": _channel_min_max(raster.channels["interior_boundary"]),
            "continuity_branch": _channel_min_max(raster.channels["continuity_branch"]),
            "base_preference_total": _channel_min_max(raster.channels["base_preference_total"]),
            "safety_soft": _channel_min_max(raster.channels["safety_soft"]),
            "rule_soft": _channel_min_max(raster.channels["rule_soft"]),
            "dynamic_soft": _channel_min_max(raster.channels["dynamic_soft"]),
        },
        "channel_display_ranges": {
            channel_name: {
                "range": resolve_display_range(
                    raster.channels[channel_name],
                    channel_name=channel_name,
                    scale_mode=scale_mode,
                ),
                "unit": display_unit(channel_name),
            }
            for channel_name in (
                "progression_tilted",
                "interior_boundary",
                "continuity_branch",
                "base_preference_total",
                "safety_soft",
                "rule_soft",
                "dynamic_soft",
            )
        },
        "hard_mask_pixel_counts": {
            "hard_unsafe_mask": int(np.sum(raster.channels["hard_unsafe_mask"])),
            "hard_rule_mask": int(np.sum(raster.channels["hard_rule_mask"])),
            "hard_dynamic_mask": int(np.sum(raster.channels["hard_dynamic_mask"])),
        },
        "channel_titles": CHANNEL_TITLES,
        "channel_descriptions": CHANNEL_DESCRIPTIONS,
        "render_file_manifest": file_manifest,
    }
    summary_path = base_out_dir / "render_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    file_manifest["render_summary.json"] = str(summary_path)
    summary["render_file_manifest"] = file_manifest
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return RenderArtifacts(out_dir=base_out_dir, file_manifest=file_manifest, summary=summary)


def render_diff_image(
    data: np.ndarray,
    extent: tuple[float, float, float, float],
    *,
    channel_name: str,
    title: str,
    out_path: Path,
    dpi: int = 160,
    scale_mode: str = SCALE_MODE_FIXED,
) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 5.8), dpi=dpi)
    value_range = resolve_display_range(data, channel_name=channel_name, scale_mode=scale_mode, diff=True)
    image = ax.imshow(
        data,
        origin="lower",
        extent=extent,
        cmap="coolwarm",
        vmin=value_range[0],
        vmax=value_range[1],
        aspect="auto",
    )
    fig.colorbar(image, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.text(
        0.90,
        0.03,
        format_display_range(channel_name, scale_mode=scale_mode, value_range=value_range, diff=True),
        va="bottom",
        ha="right",
        color="#333333",
        fontsize=8,
    )
    fig.savefig(out_path)
    plt.close(fig)
