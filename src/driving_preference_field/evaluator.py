from __future__ import annotations

"""State and trajectory composition for the current tiny evaluator.

The evaluator keeps the canonical layer split explicit:

- base preference channels are summed into base_preference_total
- soft exception channels are summed into soft_exception_total
- hard violation flags stay separate and dominate trajectory ordering
"""

from dataclasses import dataclass, field

from .channels import (
    continuity_branch,
    continuity_branch_details,
    interior_boundary,
    interior_signed_margin,
    progression_tilted_details,
)
from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample, TrajectorySample
from .exception_layers import evaluate_exception_layers


@dataclass(frozen=True)
class StateEvaluationResult:
    base_preference_channels: dict[str, float]
    soft_exception_channels: dict[str, float]
    hard_violation_flags: dict[str, bool]
    diagnostics: dict[str, object] = field(default_factory=dict)

    @property
    def base_preference_total(self) -> float:
        return sum(self.base_preference_channels.values())

    @property
    def soft_exception_total(self) -> float:
        return sum(self.soft_exception_channels.values())

    @property
    def hard_violation_count(self) -> int:
        return sum(1 for value in self.hard_violation_flags.values() if value)


@dataclass(frozen=True)
class TrajectoryEvaluationResult:
    trajectory_base_preference_channels: dict[str, float]
    trajectory_soft_exception_channels: dict[str, float]
    trajectory_hard_violation_flags: dict[str, bool]
    ordering_key: tuple[int, float, float]
    state_results: tuple[StateEvaluationResult, ...] = ()

    @property
    def trajectory_base_preference_total(self) -> float:
        return sum(self.trajectory_base_preference_channels.values())

    @property
    def trajectory_soft_exception_total(self) -> float:
        return sum(self.trajectory_soft_exception_channels.values())


def evaluate_state(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> StateEvaluationResult:
    field_config = config or DEFAULT_FIELD_CONFIG
    progression_details = progression_tilted_details(snapshot, context, state, config=field_config)
    branch_details = continuity_branch_details(snapshot, context, state, config=field_config)
    base_channels = {
        "progression_tilted": float(progression_details["score"]),
        "interior_boundary": interior_boundary(snapshot, context, state, config=field_config),
        "continuity_branch": continuity_branch(snapshot, context, state, config=field_config),
    }
    soft_channels, hard_flags = evaluate_exception_layers(snapshot, context, state)
    base_total = sum(base_channels.values())
    soft_total = sum(soft_channels.values())
    diagnostics = {
        "mode": context.mode,
        "phase": context.phase,
        "window": {
            "x_min": context.local_window.x_min,
            "x_max": context.local_window.x_max,
            "y_min": context.local_window.y_min,
            "y_max": context.local_window.y_max,
        },
        "field_config": field_config.to_dict(),
        "progression_frame": field_config.progression.longitudinal_frame,
        "progression_anchor_count": progression_details["anchor_count"],
        "progression_support_sum": progression_details["support_sum"],
        "progression_support_mod": progression_details["support_mod"],
        "progression_alignment_mod": progression_details["alignment_mod"],
        "progression_longitudinal_component": progression_details["longitudinal_component"],
        "progression_transverse_component": progression_details["transverse_component"],
        "progression_blended_progress": progression_details["blended_progress"],
        "progression_dominant_guides": progression_details["dominant_guides"],
        "interior_signed_margin": interior_signed_margin(snapshot, state),
        "nearest_branch_guide_id": branch_details["guide_id"],
        "base_preference_total": base_total,
        "soft_exception_total": soft_total,
    }
    return StateEvaluationResult(
        base_preference_channels=base_channels,
        soft_exception_channels=soft_channels,
        hard_violation_flags=hard_flags,
        diagnostics=diagnostics,
    )


def evaluate_trajectory(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    trajectory: TrajectorySample,
    *,
    config: FieldConfig | None = None,
) -> TrajectoryEvaluationResult:
    field_config = config or DEFAULT_FIELD_CONFIG
    state_results = tuple(evaluate_state(snapshot, context, state, config=field_config) for state in trajectory.states)
    base_channels = {
        "progression_tilted": sum(result.base_preference_channels["progression_tilted"] for result in state_results),
        "interior_boundary": sum(result.base_preference_channels["interior_boundary"] for result in state_results),
        "continuity_branch": sum(result.base_preference_channels["continuity_branch"] for result in state_results),
    }
    soft_channels = {
        "safety_soft": sum(result.soft_exception_channels["safety_soft"] for result in state_results),
        "rule_soft": sum(result.soft_exception_channels["rule_soft"] for result in state_results),
        "dynamic_soft": sum(result.soft_exception_channels["dynamic_soft"] for result in state_results),
    }
    hard_flags = {
        "unsafe": any(result.hard_violation_flags["unsafe"] for result in state_results),
        "rule_blocked": any(result.hard_violation_flags["rule_blocked"] for result in state_results),
        "dynamic_blocked": any(result.hard_violation_flags["dynamic_blocked"] for result in state_results),
    }
    hard_count = sum(1 for value in hard_flags.values() if value)
    soft_total = sum(soft_channels.values())
    base_total = sum(base_channels.values())
    return TrajectoryEvaluationResult(
        trajectory_base_preference_channels=base_channels,
        trajectory_soft_exception_channels=soft_channels,
        trajectory_hard_violation_flags=hard_flags,
        ordering_key=(hard_count, soft_total, -base_total),
        state_results=state_results,
    )
