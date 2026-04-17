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
    "progression_s_hat": "Blended progression coordinate over the local space. This is the current implementation debug view of s_hat.",
    "progression_n_hat": "Signed lateral offset from a smooth same-guide cross-section chosen around the nearest guide branch. Lower absolute value means closer to that guide geometry.",
    "progression_longitudinal_component": "Current implementation longitudinal tilt term before gain is applied.",
    "progression_transverse_component": "Current implementation center-high transverse profile term.",
    "progression_support_mod": "Weak secondary support modulation. It should not dominate the space shape.",
    "progression_alignment_mod": "Weak secondary heading-alignment modulation. It should not dominate the space shape.",
    "safety_soft": "Distance-based obstacle cost from safety regions. Higher means stronger obstacle costmap response.",
    "rule_soft": "Rule-related cost from regulation or non-drivable rule regions.",
    "dynamic_soft": "Dynamic interaction cost from predicted moving-object influence regions.",
    "hard_unsafe_mask": "Binary mask for hard unsafe states.",
    "hard_rule_mask": "Binary mask for hard rule-blocked states.",
    "hard_dynamic_mask": "Binary mask for hard dynamic-blocked states.",
}

CHANNEL_TITLES = {
    "progression_tilted": "Progression Tilted",
    "progression_s_hat": "Progression s_hat",
    "progression_n_hat": "Progression n_hat",
    "progression_longitudinal_component": "Longitudinal Component",
    "progression_transverse_component": "Transverse Component",
    "progression_support_mod": "Support Modulation",
    "progression_alignment_mod": "Alignment Modulation",
    "safety_soft": "Obstacle Cost",
    "rule_soft": "Rule Cost",
    "dynamic_soft": "Dynamic Cost",
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
        raster.channels["progression_tilted"],
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
        "safety_soft",
        "rule_soft",
        "dynamic_soft",
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
            "  cyan = progression guide",
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
        "progression_s_hat.png": ("progression_s_hat", CHANNEL_TITLES["progression_s_hat"], "viridis"),
        "progression_n_hat.png": ("progression_n_hat", CHANNEL_TITLES["progression_n_hat"], "magma"),
        "progression_longitudinal_component.png": (
            "progression_longitudinal_component",
            CHANNEL_TITLES["progression_longitudinal_component"],
            "plasma",
        ),
        "progression_transverse_component.png": (
            "progression_transverse_component",
            CHANNEL_TITLES["progression_transverse_component"],
            "cividis",
        ),
        "progression_support_mod.png": (
            "progression_support_mod",
            CHANNEL_TITLES["progression_support_mod"],
            "inferno",
        ),
        "progression_alignment_mod.png": (
            "progression_alignment_mod",
            CHANNEL_TITLES["progression_alignment_mod"],
            "inferno",
        ),
        "safety_soft.png": ("safety_soft", CHANNEL_TITLES["safety_soft"], "inferno"),
        "rule_soft.png": ("rule_soft", CHANNEL_TITLES["rule_soft"], "magma"),
        "dynamic_soft.png": ("dynamic_soft", CHANNEL_TITLES["dynamic_soft"], "cividis"),
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
            "progression_s_hat": _channel_min_max(raster.channels["progression_s_hat"]),
            "progression_n_hat": _channel_min_max(raster.channels["progression_n_hat"]),
            "progression_longitudinal_component": _channel_min_max(raster.channels["progression_longitudinal_component"]),
            "progression_transverse_component": _channel_min_max(raster.channels["progression_transverse_component"]),
            "progression_support_mod": _channel_min_max(raster.channels["progression_support_mod"]),
            "progression_alignment_mod": _channel_min_max(raster.channels["progression_alignment_mod"]),
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
                "progression_s_hat",
                "progression_n_hat",
                "progression_longitudinal_component",
                "progression_transverse_component",
                "progression_support_mod",
                "progression_alignment_mod",
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
