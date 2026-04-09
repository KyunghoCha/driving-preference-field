from __future__ import annotations

"""Fast cached runtime query layer for downstream consumers.

This module keeps the SSOT-side field semantics in one place while exposing a
runtime object that can answer repeated state, trajectory, and debug-grid
queries without rebuilding progression internals for every call.
"""

from dataclasses import dataclass

import numpy as np

from .channels import continuity_branch_details, interior_boundary, interior_signed_margin
from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample, TrajectorySample
from .exception_layers import evaluate_exception_layers
from .progression_surface import ProgressionSurfaceRuntime, build_progression_surface_runtime


@dataclass(frozen=True)
class FieldStateQueryResult:
    base_channels: dict[str, float]
    soft_channels: dict[str, float]
    hard_flags: dict[str, bool]
    diagnostics: dict[str, object]


@dataclass(frozen=True)
class FieldTrajectoryQueryResult:
    base_channels: dict[str, float]
    soft_channels: dict[str, float]
    hard_flags: dict[str, bool]
    ordering_key: tuple[int, float, float]
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
        branch_details = continuity_branch_details(self.snapshot, self.context, state, config=self.config)
        base_channels = {
            "progression_tilted": float(progression_details["score"]),
            "interior_boundary": interior_boundary(self.snapshot, self.context, state, config=self.config),
            "continuity_branch": float(branch_details["score"]),
        }
        soft_channels, hard_flags = evaluate_exception_layers(self.snapshot, self.context, state)
        base_total = sum(base_channels.values())
        soft_total = sum(soft_channels.values())
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
            "interior_signed_margin": interior_signed_margin(self.snapshot, state),
            "nearest_branch_guide_id": branch_details["guide_id"],
            "base_preference_total": base_total,
            "soft_exception_total": soft_total,
        }
        return FieldStateQueryResult(
            base_channels=base_channels,
            soft_channels=soft_channels,
            hard_flags=hard_flags,
            diagnostics=diagnostics,
        )

    def query_trajectory(self, trajectory: TrajectorySample) -> FieldTrajectoryQueryResult:
        state_results = tuple(self.query_state(state) for state in trajectory.states)
        base_channels = {
            "progression_tilted": sum(result.base_channels["progression_tilted"] for result in state_results),
            "interior_boundary": sum(result.base_channels["interior_boundary"] for result in state_results),
            "continuity_branch": sum(result.base_channels["continuity_branch"] for result in state_results),
        }
        soft_channels = {
            "safety_soft": sum(result.soft_channels["safety_soft"] for result in state_results),
            "rule_soft": sum(result.soft_channels["rule_soft"] for result in state_results),
            "dynamic_soft": sum(result.soft_channels["dynamic_soft"] for result in state_results),
        }
        hard_flags = {
            "unsafe": any(result.hard_flags["unsafe"] for result in state_results),
            "rule_blocked": any(result.hard_flags["rule_blocked"] for result in state_results),
            "dynamic_blocked": any(result.hard_flags["dynamic_blocked"] for result in state_results),
        }
        hard_count = sum(1 for value in hard_flags.values() if value)
        soft_total = sum(soft_channels.values())
        base_total = sum(base_channels.values())
        return FieldTrajectoryQueryResult(
            base_channels=base_channels,
            soft_channels=soft_channels,
            hard_flags=hard_flags,
            ordering_key=(hard_count, soft_total, -base_total),
            state_results=state_results,
        )

    def query_debug_grid(self, x_coords: np.ndarray, y_coords: np.ndarray) -> dict[str, np.ndarray]:
        shape = (len(y_coords), len(x_coords))
        progression_grid = self.progression_runtime.query_grid(x_coords, y_coords)
        channels: dict[str, np.ndarray] = {
            "progression_tilted": progression_grid["score"],
            "progression_s_hat": progression_grid["s_hat"],
            "progression_n_hat": progression_grid["n_hat"],
            "progression_longitudinal_component": progression_grid["longitudinal_component"],
            "progression_transverse_component": progression_grid["transverse_component"],
            "progression_support_mod": progression_grid["support_mod"],
            "progression_alignment_mod": progression_grid["alignment_mod"],
            "interior_boundary": np.zeros(shape, dtype=float),
            "continuity_branch": np.zeros(shape, dtype=float),
            "base_preference_total": np.zeros(shape, dtype=float),
            "safety_soft": np.zeros(shape, dtype=float),
            "rule_soft": np.zeros(shape, dtype=float),
            "dynamic_soft": np.zeros(shape, dtype=float),
            "hard_unsafe_mask": np.zeros(shape, dtype=bool),
            "hard_rule_mask": np.zeros(shape, dtype=bool),
            "hard_dynamic_mask": np.zeros(shape, dtype=bool),
        }

        for yi, y in enumerate(y_coords):
            for xi, x in enumerate(x_coords):
                state = StateSample(x=float(x), y=float(y), yaw=self.context.ego_pose.yaw)
                interior_value = interior_boundary(self.snapshot, self.context, state, config=self.config)
                branch_value = float(
                    continuity_branch_details(self.snapshot, self.context, state, config=self.config)["score"]
                )
                soft_channels, hard_flags = evaluate_exception_layers(self.snapshot, self.context, state)
                channels["interior_boundary"][yi, xi] = interior_value
                channels["continuity_branch"][yi, xi] = branch_value
                channels["base_preference_total"][yi, xi] = (
                    channels["progression_tilted"][yi, xi] + interior_value + branch_value
                )
                channels["safety_soft"][yi, xi] = soft_channels["safety_soft"]
                channels["rule_soft"][yi, xi] = soft_channels["rule_soft"]
                channels["dynamic_soft"][yi, xi] = soft_channels["dynamic_soft"]
                channels["hard_unsafe_mask"][yi, xi] = hard_flags["unsafe"]
                channels["hard_rule_mask"][yi, xi] = hard_flags["rule_blocked"]
                channels["hard_dynamic_mask"][yi, xi] = hard_flags["dynamic_blocked"]
        return channels


def build_field_runtime(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    *,
    config: FieldConfig | None = None,
) -> FieldRuntime:
    return FieldRuntime(snapshot, context, config=config)
