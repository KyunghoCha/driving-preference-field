from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProgressionConfig:
    longitudinal_frame: str = "local_absolute"
    longitudinal_family: str = "tanh"
    longitudinal_gain: float = 1.0
    lookahead_scale: float = 0.25
    longitudinal_shape: float = 1.0
    transverse_family: str = "exponential"
    transverse_scale: float = 1.0
    transverse_shape: float = 1.0
    support_ceiling: float = 1.0


@dataclass(frozen=True)
class SurfaceTuningConfig:
    anchor_spacing_m: float = 0.20
    spline_sample_density_m: float = 0.05
    spline_min_subdivisions: int = 8
    min_sigma_t: float = 0.40
    min_sigma_n: float = 0.35
    sigma_t_scale: float = 0.35
    sigma_n_scale: float = 1.50
    end_extension_m: float = 2.0
    support_base: float = 0.95
    support_range: float = 0.05
    alignment_base: float = 0.95
    alignment_range: float = 0.05
    transverse_handoff_support_ratio: float = 0.25
    transverse_handoff_score_delta: float = 0.20
    transverse_handoff_temperature: float = 0.05


@dataclass(frozen=True)
class FieldConfig:
    progression: ProgressionConfig = field(default_factory=ProgressionConfig)
    surface_tuning: SurfaceTuningConfig = field(default_factory=SurfaceTuningConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FieldConfig":
        progression = ProgressionConfig(**dict(payload.get("progression", {}) or {}))
        surface_tuning = SurfaceTuningConfig(**dict(payload.get("surface_tuning", {}) or {}))
        return cls(progression=progression, surface_tuning=surface_tuning)


@dataclass(frozen=True)
class ComparisonPreset:
    preset_name: str
    field_config: FieldConfig
    note: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "preset_name": self.preset_name,
            "field_config": self.field_config.to_dict(),
            "note": self.note,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ComparisonPreset":
        return cls(
            preset_name=str(payload["preset_name"]),
            field_config=FieldConfig.from_dict(dict(payload["field_config"])),
            note=str(payload.get("note", "")),
            metadata=dict(payload.get("metadata", {})),
        )


def progression_family_label(progression: ProgressionConfig) -> str:
    return (
        f"{progression.longitudinal_frame}:"
        f"{progression.longitudinal_family}/{progression.transverse_family}"
    )


DEFAULT_FIELD_CONFIG = FieldConfig()
