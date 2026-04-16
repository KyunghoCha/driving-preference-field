"""Tiny analytic evaluator skeleton for driving-preference-field."""

from .config import (
    DEFAULT_FIELD_CONFIG,
    ComparisonPreset,
    FieldConfig,
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
from .input_loader import LoadedSemanticInput, detect_input_kind, load_semantic_input
from .presets import DEFAULT_PRESET_DIR, load_preset, save_preset
from .rendering import RenderArtifacts, render_case
from .source_adapter import GenericAdapterValidationError, load_generic_snapshot

__all__ = [
    "DEFAULT_FIELD_CONFIG",
    "ComparisonPreset",
    "BoundaryInteriorSupport",
    "BranchContinuitySupport",
    "DirectedPolyline",
    "DrivableSupport",
    "ExceptionLayerSupport",
    "FieldConfig",
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
    "GenericAdapterValidationError",
    "LoadedSemanticInput",
    "build_field_runtime",
    "detect_input_kind",
    "load_preset",
    "load_generic_snapshot",
    "load_semantic_input",
    "RenderArtifacts",
    "render_case",
    "save_preset",
]
