"""Tiny analytic evaluator skeleton for driving-preference-field."""

from .config import (
    DEFAULT_FIELD_CONFIG,
    ComparisonPreset,
    ContinuityBranchConfig,
    FieldConfig,
    InteriorBoundaryConfig,
    ProgressionConfig,
)
from .contracts import (
    BoundaryInteriorSupport,
    BranchContinuitySupport,
    DirectedPolyline,
    DrivableSupport,
    ExceptionLayerSupport,
    PolygonRegion,
    ProgressionSupport,
    QueryContext,
    QueryWindow,
    SemanticInputSnapshot,
    StateSample,
    TrajectorySample,
)
from .evaluator import (
    StateEvaluationResult,
    TrajectoryEvaluationResult,
    evaluate_state,
    evaluate_trajectory,
)
from .field_runtime import FieldRuntime, build_field_runtime
from .presets import DEFAULT_PRESET_DIR, load_preset, save_preset
from .rendering import RenderArtifacts, render_case

__all__ = [
    "DEFAULT_FIELD_CONFIG",
    "ComparisonPreset",
    "ContinuityBranchConfig",
    "BoundaryInteriorSupport",
    "BranchContinuitySupport",
    "DirectedPolyline",
    "DrivableSupport",
    "ExceptionLayerSupport",
    "FieldConfig",
    "InteriorBoundaryConfig",
    "PolygonRegion",
    "ProgressionConfig",
    "ProgressionSupport",
    "QueryContext",
    "QueryWindow",
    "SemanticInputSnapshot",
    "StateEvaluationResult",
    "StateSample",
    "TrajectoryEvaluationResult",
    "TrajectorySample",
    "DEFAULT_PRESET_DIR",
    "evaluate_state",
    "evaluate_trajectory",
    "FieldRuntime",
    "build_field_runtime",
    "load_preset",
    "RenderArtifacts",
    "render_case",
    "save_preset",
]
