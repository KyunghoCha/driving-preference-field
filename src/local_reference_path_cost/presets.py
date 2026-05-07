from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import ComparisonPreset, progression_family_label


DEFAULT_PRESET_DIR = Path("presets/lab")
DEFAULT_BASELINE_PRESET_NAME = "baseline__balanced_field"
DEFAULT_CANDIDATE_PRESET_NAME = "candidate__strong_longitudinal"


@dataclass(frozen=True)
class PresetDescriptor:
    path: Path
    preset: ComparisonPreset
    role: str | None
    origin: str
    label: str
    family: str
    description: str
    is_reference: bool

    @property
    def display_name(self) -> str:
        suffix = " [ref]" if self.is_reference else ""
        return f"{self.label}{suffix}"


def list_presets(preset_dir: Path | str = DEFAULT_PRESET_DIR) -> list[Path]:
    root = Path(preset_dir)
    if not root.exists():
        return []
    return sorted(root.glob("*.yaml"))


def describe_preset(path: Path | str) -> PresetDescriptor:
    preset_path = Path(path)
    preset = load_preset(preset_path)
    metadata = dict(preset.metadata)
    role_raw = metadata.get("role")
    role = str(role_raw).strip() if role_raw is not None and str(role_raw).strip() else None
    origin = str(metadata.get("origin", "user"))
    label = str(metadata.get("label", preset.preset_name))
    family = str(metadata.get("family", progression_family_label(preset.field_config.progression)))
    description = str(metadata.get("description", ""))
    return PresetDescriptor(
        path=preset_path,
        preset=preset,
        role=role,
        origin=origin,
        label=label,
        family=family,
        description=description,
        is_reference=(origin == "reference"),
    )


def indexed_presets(preset_dir: Path | str = DEFAULT_PRESET_DIR) -> list[PresetDescriptor]:
    return [describe_preset(path) for path in list_presets(preset_dir)]


def presets_for_role(
    role: str,
    preset_dir: Path | str = DEFAULT_PRESET_DIR,
) -> list[PresetDescriptor]:
    descriptors = indexed_presets(preset_dir)
    return [descriptor for descriptor in descriptors if descriptor.role in (None, role)]


def find_preset_path(
    preset_name: str,
    preset_dir: Path | str = DEFAULT_PRESET_DIR,
) -> Path | None:
    for path in list_presets(preset_dir):
        if path.stem == preset_name or path.name == preset_name:
            return path
    return None


def default_preset_path(
    role: str,
    preset_dir: Path | str = DEFAULT_PRESET_DIR,
) -> Path | None:
    preset_name = DEFAULT_BASELINE_PRESET_NAME if role == "baseline" else DEFAULT_CANDIDATE_PRESET_NAME
    return find_preset_path(preset_name, preset_dir)


def can_overwrite_preset(path: Path | str) -> tuple[bool, str | None]:
    target = Path(path)
    if not target.exists():
        return True, None
    try:
        descriptor = describe_preset(target)
    except Exception:  # noqa: BLE001
        return True, None
    if descriptor.is_reference:
        return False, "reference preset은 덮어쓸 수 없습니다. 새 이름으로 저장하세요."
    return True, None


def save_preset(preset: ComparisonPreset, path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(preset.to_dict(), sort_keys=False), encoding="utf-8")
    return target


def load_preset(path: Path | str) -> ComparisonPreset:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return ComparisonPreset.from_dict(dict(payload))
