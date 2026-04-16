from __future__ import annotations

"""Fast cached runtime query layer for downstream consumers.

This module exposes the progression-centered public runtime contract. Costmap
and burden visualization remain in raster/rendering paths and are not part of
the public runtime payload.
"""

from dataclasses import dataclass

import numpy as np

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample, TrajectorySample
from .progression_surface import ProgressionSurfaceRuntime, build_progression_surface_runtime


@dataclass(frozen=True)
class FieldStateQueryResult:
    base_channels: dict[str, float]
    diagnostics: dict[str, object]


@dataclass(frozen=True)
class FieldTrajectoryQueryResult:
    base_channels: dict[str, float]
    ordering_key: tuple[float]
    state_results: tuple[FieldStateQueryResult, ...]


class FieldRuntime:
    """Cached field runtime for repeated state, trajectory, and grid queries."""

    def __init__(
        self,
        snapshot: SemanticInputSnapshot,
        context: QueryContext,
        *,
        config: FieldConfig | None = None,
    ) -> None:
        self.snapshot = snapshot
        self.context = context
        self.config = config or DEFAULT_FIELD_CONFIG
        self.progression_runtime: ProgressionSurfaceRuntime = build_progression_surface_runtime(
            snapshot,
            context,
            config=self.config.progression,
        )

    def query_state(self, state: StateSample) -> FieldStateQueryResult:
        progression_details = self.progression_runtime.query_state(state)
        base_channels = {
            "progression_tilted": float(progression_details["score"]),
        }
        base_total = sum(base_channels.values())
        diagnostics = {
            "mode": self.context.mode,
            "phase": self.context.phase,
            "window": {
                "x_min": self.context.local_window.x_min,
                "x_max": self.context.local_window.x_max,
                "y_min": self.context.local_window.y_min,
                "y_max": self.context.local_window.y_max,
            },
            "field_config": self.config.to_dict(),
            "progression_frame": self.config.progression.longitudinal_frame,
            "progression_anchor_count": progression_details["anchor_count"],
            "progression_support_sum": progression_details["support_sum"],
            "progression_support_mod": progression_details["support_mod"],
            "progression_alignment_mod": progression_details["alignment_mod"],
            "progression_longitudinal_component": progression_details["longitudinal_component"],
            "progression_transverse_component": progression_details["transverse_component"],
            "progression_s_hat": progression_details["s_hat"],
            "progression_n_hat": progression_details["n_hat"],
            "progression_blended_progress": progression_details["blended_progress"],
            "progression_dominant_guides": progression_details["dominant_guides"],
            "base_preference_total": base_total,
        }
        return FieldStateQueryResult(
            base_channels=base_channels,
            diagnostics=diagnostics,
        )

    def query_trajectory(self, trajectory: TrajectorySample) -> FieldTrajectoryQueryResult:
        state_results = tuple(self.query_state(state) for state in trajectory.states)
        base_channels = {
            "progression_tilted": sum(result.base_channels["progression_tilted"] for result in state_results),
        }
        base_total = sum(base_channels.values())
        return FieldTrajectoryQueryResult(
            base_channels=base_channels,
            ordering_key=(-base_total,),
            state_results=state_results,
        )

    def query_progression_points(
        self,
        x_values: np.ndarray,
        y_values: np.ndarray,
        heading_yaws: np.ndarray | None = None,
    ) -> dict[str, np.ndarray]:
        return self.progression_runtime.query_points(x_values, y_values, heading_yaws)

    def query_progression_trajectories(
        self,
        trajectories_xy: np.ndarray,
        heading_yaws: np.ndarray | None = None,
    ) -> dict[str, np.ndarray]:
        return self.progression_runtime.query_trajectories(trajectories_xy, heading_yaws)

    def query_debug_grid(self, x_coords: np.ndarray, y_coords: np.ndarray) -> dict[str, np.ndarray]:
        progression_grid = self.progression_runtime.query_grid(x_coords, y_coords)
        return {
            "progression_tilted": progression_grid["score"],
            "progression_s_hat": progression_grid["s_hat"],
            "progression_n_hat": progression_grid["n_hat"],
            "progression_longitudinal_component": progression_grid["longitudinal_component"],
            "progression_transverse_component": progression_grid["transverse_component"],
            "progression_support_mod": progression_grid["support_mod"],
            "progression_alignment_mod": progression_grid["alignment_mod"],
        }


def build_field_runtime(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig | None = None,
) -> FieldRuntime:
    return FieldRuntime(snapshot, context, config=config)
