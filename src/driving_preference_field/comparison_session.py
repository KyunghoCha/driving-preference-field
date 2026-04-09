from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import ComparisonPreset


@dataclass(frozen=True)
class ComparisonSession:
    case_path: str
    selected_channel: str
    effective_ego_pose: dict[str, float]
    effective_local_window: dict[str, float]
    baseline_preset: ComparisonPreset
    candidate_preset: ComparisonPreset
    baseline_state_summary: dict[str, Any]
    candidate_state_summary: dict[str, Any]
    diff_summary: dict[str, Any]
    profile_summary: dict[str, Any]
    baseline_render_summary: dict[str, Any]
    candidate_render_summary: dict[str, Any]
    note: str
    exported_at: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["baseline_preset"] = self.baseline_preset.to_dict()
        payload["candidate_preset"] = self.candidate_preset.to_dict()
        return payload
