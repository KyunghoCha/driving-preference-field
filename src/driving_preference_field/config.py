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
class FieldConfig:
    progression: ProgressionConfig = field(default_factory=ProgressionConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FieldConfig":
        progression = ProgressionConfig(**payload.get("progression", {}))
        return cls(progression=progression)


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
