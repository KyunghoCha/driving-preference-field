#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from local_reference_path_cost.field_runtime import build_field_runtime
from local_reference_path_cost.planner_lookup import build_progression_lookup, query_progression_lookup_trajectories
from local_reference_path_cost.toy_loader import load_toy_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark internal scalar lookup vs exact progression query.")
    parser.add_argument("--case", default="u_turn", help="toy case name under cases/toy")
    parser.add_argument("--batch", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=32)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--grid-spacing", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--export-dir", type=Path, default=None)
    args = parser.parse_args()

    snapshot, context = load_toy_snapshot(REPO_ROOT / f"cases/toy/{args.case}.yaml")
    runtime = build_field_runtime(snapshot, context)
    trajectories_xy = _random_trajectories(context, batch=args.batch, steps=args.steps, seed=args.seed)

    build_start = time.perf_counter()
    prepared = build_progression_lookup(snapshot, context, grid_spacing_m=args.grid_spacing)
    build_time = time.perf_counter() - build_start

    exact_time, exact_scores = _timed(
        lambda: runtime.query_progression_trajectories(trajectories_xy)["progression_tilted"],
        repeats=args.repeats,
    )
    lookup_time, lookup_scores = _timed(
        lambda: query_progression_lookup_trajectories(prepared, trajectories_xy),
        repeats=args.repeats,
    )

    eval_x, eval_y = _eval_grid(context, spacing=args.grid_spacing * 0.5)
    exact_grid = runtime.query_debug_grid(eval_x, eval_y)["progression_tilted"]
    lookup_grid = query_progression_lookup_trajectories(
        prepared,
        np.stack(np.meshgrid(eval_x, eval_y), axis=-1).reshape(1, -1, 2),
    ).reshape(len(eval_y), len(eval_x))
    diff_grid = lookup_grid - exact_grid

    per_state_exact = exact_time / float(args.batch * args.steps)
    per_state_lookup = lookup_time / float(args.batch * args.steps)
    top_k = min(10, args.batch)
    exact_rank = np.argsort(np.sum(exact_scores, axis=1))[-top_k:]
    lookup_rank = np.argsort(np.sum(lookup_scores, axis=1))[-top_k:]
    overlap = len(set(exact_rank.tolist()) & set(lookup_rank.tolist()))

    print(f"case={args.case}")
    print(f"lookup_build_s={build_time:.6f}")
    print(f"exact_query_s={exact_time:.6f}")
    print(f"lookup_query_s={lookup_time:.6f}")
    print(f"exact_us_per_state={per_state_exact * 1e6:.3f}")
    print(f"lookup_us_per_state={per_state_lookup * 1e6:.3f}")
    print(f"speedup={exact_time / max(lookup_time, 1e-12):.2f}x")
    print(
        "diff_summary "
        f"max_abs={float(np.max(np.abs(diff_grid))):.6f} "
        f"mean_abs={float(np.mean(np.abs(diff_grid))):.6f}"
    )
    print(f"top_{top_k}_overlap={overlap}/{top_k}")

    if args.export_dir is not None:
        args.export_dir.mkdir(parents=True, exist_ok=True)
        np.save(args.export_dir / "exact_grid.npy", exact_grid)
        np.save(args.export_dir / "lookup_grid.npy", lookup_grid)
        np.save(args.export_dir / "diff_grid.npy", diff_grid)


def _timed(fn, *, repeats: int) -> tuple[float, np.ndarray]:
    best_time = None
    best_value = None
    for _ in range(max(repeats, 1)):
        start = time.perf_counter()
        value = fn()
        elapsed = time.perf_counter() - start
        if best_time is None or elapsed < best_time:
            best_time = elapsed
            best_value = value
    assert best_time is not None and best_value is not None
    return float(best_time), best_value


def _random_trajectories(context, *, batch: int, steps: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    xs = rng.uniform(context.local_window.x_min, context.local_window.x_max, size=(batch, steps))
    ys = rng.uniform(context.local_window.y_min, context.local_window.y_max, size=(batch, steps))
    return np.stack([xs, ys], axis=-1)


def _eval_grid(context, *, spacing: float) -> tuple[np.ndarray, np.ndarray]:
    x_coords = _metric_coords(context.local_window.x_min, context.local_window.x_max, spacing)
    y_coords = _metric_coords(context.local_window.y_min, context.local_window.y_max, spacing)
    return x_coords, y_coords


def _metric_coords(start: float, stop: float, spacing: float) -> np.ndarray:
    count = int(np.floor((stop - start) / spacing)) + 1
    coords = start + spacing * np.arange(count, dtype=float)
    if coords[-1] < stop - 1e-9:
        coords = np.append(coords, float(stop))
    else:
        coords[-1] = float(stop)
    return coords


if __name__ == "__main__":
    main()
