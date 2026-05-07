from __future__ import annotations

"""State and trajectory composition for the current tiny evaluator.

The public evaluator payload is progression-centered. Costmap-style burdens
remain available only through raster/rendering visualization paths.
"""

from dataclasses import dataclass, field

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample, TrajectorySample
from .field_runtime import build_field_runtime


@dataclass(frozen=True)
class StateEvaluationResult:
    base_preference_channels: dict[str, float]
    diagnostics: dict[str, object] = field(default_factory=dict)

    @property
    def base_preference_total(self) -> float:
        return sum(self.base_preference_channels.values())

@dataclass(frozen=True)
class TrajectoryEvaluationResult:
    trajectory_base_preference_channels: dict[str, float]
    ordering_key: tuple[float]
    state_results: tuple[StateEvaluationResult, ...] = ()

    @property
    def trajectory_base_preference_total(self) -> float:
        return sum(self.trajectory_base_preference_channels.values())

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
        ordering_key=payload.ordering_key,
        state_results=tuple(
            StateEvaluationResult(
                base_preference_channels=state.base_channels,
                diagnostics=state.diagnostics,
            )
            for state in payload.state_results
        ),
    )
