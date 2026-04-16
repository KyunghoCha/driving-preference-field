from __future__ import annotations

"""Progression-centered base field channels.

The project-level formulas are documented in
docs/reference/current_formula_reference_ko.md. This module only exposes the
active base channels that remain part of the public contract.
"""
from typing import Any

from .config import DEFAULT_FIELD_CONFIG, FieldConfig
from .contracts import QueryContext, SemanticInputSnapshot, StateSample
from .progression_surface import progression_surface_details


def progression_tilted_details(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> dict[str, Any]:
    field_config = config or DEFAULT_FIELD_CONFIG
    return progression_surface_details(
        snapshot,
        context,
        state,
        config=field_config,
    )


def progression_tilted(
    snapshot: SemanticInputSnapshot,
    context: QueryContext,
    state: StateSample,
    *,
    config: FieldConfig | None = None,
) -> float:
    return float(progression_tilted_details(snapshot, context, state, config=config)["score"])
