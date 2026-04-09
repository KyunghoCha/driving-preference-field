from __future__ import annotations

"""State and trajectory composition for the current tiny evaluator.

The evaluator keeps the canonical layer split explicit:

- base preference channels are summed into base_preference_total
- soft exception channels are summed into soft_exception_total
- hard violation flags stay separate and dominate trajectory ordering
"""

from dataclasses import dataclass, field

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample, TrajectorySample
from .field_runtime import build_field_runtime


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
    payload = build_field_runtime(snapshot, context, config=field_config).query_state(state)
    return StateEvaluationResult(
        base_preference_channels=payload.base_channels,
        soft_exception_channels=payload.soft_channels,
        hard_violation_flags=payload.hard_flags,
        diagnostics=payload.diagnostics,
    )


def evaluate_trajectory(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    trajectory: TrajectorySample,
    *,
    config: FieldConfig | None = None,
) -> TrajectoryEvaluationResult:
    field_config = config or DEFAULT_FIELD_CONFIG
    payload = build_field_runtime(snapshot, context, config=field_config).query_trajectory(trajectory)
    return TrajectoryEvaluationResult(
        trajectory_base_preference_channels=payload.base_channels,
        trajectory_soft_exception_channels=payload.soft_channels,
        trajectory_hard_violation_flags=payload.hard_flags,
        ordering_key=payload.ordering_key,
        state_results=tuple(
            StateEvaluationResult(
                base_preference_channels=state.base_channels,
                soft_exception_channels=state.soft_channels,
                hard_violation_flags=state.hard_flags,
                diagnostics=state.diagnostics,
            )
            for state in payload.state_results
        ),
    )
