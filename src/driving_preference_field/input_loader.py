from __future__ import annotations

"""Loader dispatch for toy cases and generic adapter inputs."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import yaml

from .contracts import QueryContext, SemanticInputSnapshot
from .source_adapter import load_generic_snapshot
from .toy_loader import load_toy_snapshot, summarize_snapshot


@dataclass(frozen=True)
class LoadedSemanticInput:
    snapshot: SemanticInputSnapshot
    context: QueryContext
    input_kind: str


def _read_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a top-level mapping")
    return dict(payload)


def detect_input_kind(input_path: str | Path) -> str:
    path = Path(input_path)
    payload = _read_mapping(path)
    if "query_context" in payload or "progression_supports" in payload:
        return "generic_adapter"
    return "toy_case"


def load_semantic_input(input_path: str | Path) -> LoadedSemanticInput:
    path = Path(input_path)
    kind = detect_input_kind(path)
    if kind == "generic_adapter":
        snapshot, context = load_generic_snapshot(path)
    else:
        snapshot, context = load_toy_snapshot(path)
    return LoadedSemanticInput(snapshot=snapshot, context=context, input_kind=kind)


def summarize_loaded_input(loaded: LoadedSemanticInput) -> dict[str, Any]:
    return {
        "input_kind": loaded.input_kind,
        "summary": summarize_snapshot(loaded.snapshot),
        "query_context": {
            "ego_pose": {
                "x": loaded.context.ego_pose.x,
                "y": loaded.context.ego_pose.y,
                "yaw": loaded.context.ego_pose.yaw,
            },
            "local_window": {
                "x_min": loaded.context.local_window.x_min,
                "x_max": loaded.context.local_window.x_max,
                "y_min": loaded.context.local_window.y_min,
                "y_max": loaded.context.local_window.y_max,
            },
            "mode": loaded.context.mode,
            "phase": loaded.context.phase,
        },
    }
