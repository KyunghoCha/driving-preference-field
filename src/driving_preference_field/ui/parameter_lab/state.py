from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from driving_preference_field.config import (
    ComparisonPreset,
    DEFAULT_FIELD_CONFIG,
    FieldConfig,
    progression_family_label,
)
from driving_preference_field.contracts import QueryContext, QueryWindow, StateSample
from driving_preference_field.input_loader import load_semantic_input
from driving_preference_field.presets import (
    DEFAULT_PRESET_DIR,
    can_overwrite_preset,
    default_preset_path,
    indexed_presets,
    load_preset,
    save_preset,
)


@dataclass
class PresetSideState:
    preset_name: str
    note: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    source_path: Path | None = None
    unsaved: bool = False

    def display_name(self) -> str:
        return f"{self.preset_name} (unsaved)" if self.unsaved else self.preset_name

    def to_preset(self, config: FieldConfig, *, side: str) -> ComparisonPreset:
        metadata = dict(self.metadata)
        metadata["role"] = side
        metadata.setdefault("label", self.preset_name)
        metadata.setdefault("family", progression_family_label(config.progression))
        metadata["origin"] = "user" if self.unsaved else str(metadata.get("origin", "user"))
        metadata["unsaved"] = self.unsaved
        return ComparisonPreset(
            preset_name=self.preset_name,
            field_config=config,
            note=self.note,
            metadata=metadata,
        )


class ParameterLabState:
    def __init__(
        self,
        *,
        repo_root: Path,
        case_path: Path | None = None,
        baseline_preset: Path | None = None,
        candidate_preset: Path | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.cases_root = self.repo_root / "cases/toy"
        self.fixture_root = self.repo_root / "fixtures/adapter"
        self.preset_root = self.repo_root / DEFAULT_PRESET_DIR
        self.preset_root.mkdir(parents=True, exist_ok=True)

        self.current_case_path = Path()
        self.current_input_kind = ""
        self.snapshot = None
        self.default_context: QueryContext | None = None
        self.working_context: QueryContext | None = None

        self.baseline_state = PresetSideState(preset_name="baseline_default")
        self.candidate_state = PresetSideState(preset_name="candidate_default")
        self.baseline_config = DEFAULT_FIELD_CONFIG
        self.candidate_config = DEFAULT_FIELD_CONFIG

        self.initialize_side_from_path("baseline", Path(baseline_preset) if baseline_preset else None)
        self.initialize_side_from_path("candidate", Path(candidate_preset) if candidate_preset else None)

        case_candidates = self.available_case_paths()
        if not case_candidates and case_path is None:
            raise RuntimeError(
                f"no parameter lab cases found under {self.cases_root} or {self.fixture_root}"
            )
        initial_case = self.normalize_case_path(Path(case_path) if case_path is not None else case_candidates[0])
        self.load_case(initial_case)

    def update_repo_root(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.cases_root = self.repo_root / "cases/toy"
        self.fixture_root = self.repo_root / "fixtures/adapter"

    def update_preset_root(self, preset_root: Path) -> None:
        self.preset_root = preset_root.resolve()
        self.preset_root.mkdir(parents=True, exist_ok=True)

    def normalize_case_path(self, case_path: Path | str) -> Path:
        candidate = Path(case_path)
        if candidate.is_absolute():
            return candidate.resolve()
        repo_relative = (self.repo_root / candidate).resolve()
        if repo_relative.exists():
            return repo_relative
        cases_relative = (self.cases_root / candidate).resolve()
        if cases_relative.exists():
            return cases_relative
        fixture_relative = (self.fixture_root / candidate).resolve()
        if fixture_relative.exists():
            return fixture_relative
        return candidate.resolve()

    def available_case_paths(self) -> list[Path]:
        return sorted(self.cases_root.glob("*.yaml")) + sorted(self.fixture_root.glob("*.yaml"))

    def initialize_side_from_path(self, side: str, preset_path: Path | None) -> None:
        resolved_path = preset_path
        if resolved_path is None or not resolved_path.exists():
            resolved_path = default_preset_path(side, self.preset_root)
        if resolved_path is None or not resolved_path.exists():
            return
        preset = load_preset(resolved_path)
        self.set_side_from_preset(side, preset, source_path=resolved_path, unsaved=False)

    def set_side_from_preset(
        self,
        side: str,
        preset: ComparisonPreset,
        *,
        source_path: Path | None,
        unsaved: bool,
    ) -> None:
        state = PresetSideState(
            preset_name=preset.preset_name,
            note=preset.note,
            metadata=dict(preset.metadata),
            source_path=source_path,
            unsaved=unsaved,
        )
        if side == "baseline":
            self.baseline_state = state
            self.baseline_config = preset.field_config
        else:
            self.candidate_state = state
            self.candidate_config = preset.field_config

    def mark_side_unsaved(self, side: str) -> None:
        state = self.baseline_state if side == "baseline" else self.candidate_state
        metadata = dict(state.metadata)
        metadata["role"] = side
        metadata["origin"] = "user"
        metadata.setdefault("label", state.preset_name)
        updated = PresetSideState(
            preset_name=state.preset_name,
            note=state.note,
            metadata=metadata,
            source_path=state.source_path,
            unsaved=True,
        )
        if side == "baseline":
            self.baseline_state = updated
        else:
            self.candidate_state = updated

    def load_case(self, case_path: Path | str) -> None:
        resolved = self.normalize_case_path(case_path)
        loaded = load_semantic_input(resolved)
        self.snapshot = loaded.snapshot
        self.current_case_path = resolved
        self.current_input_kind = loaded.input_kind
        self.default_context = loaded.context
        self.working_context = loaded.context

    def reload_case(self) -> None:
        self.load_case(self.current_case_path)

    def apply_case_controls(self, ego_pose: StateSample, local_window: QueryWindow) -> None:
        assert self.snapshot is not None and self.default_context is not None
        self.working_context = QueryContext(
            semantic_snapshot=self.snapshot,
            ego_pose=ego_pose,
            local_window=local_window,
            mode=self.default_context.mode,
            phase=self.default_context.phase,
        )

    def reset_case_controls(self) -> None:
        assert self.default_context is not None
        self.working_context = self.default_context

    def update_side_config(self, side: str, config: FieldConfig) -> None:
        if side == "baseline":
            self.baseline_config = config
        else:
            self.candidate_config = config
        self.mark_side_unsaved(side)

    def load_preset_into_side(self, side: str, preset_path: Path | str) -> None:
        preset = load_preset(preset_path)
        self.set_side_from_preset(side, preset, source_path=Path(preset_path), unsaved=False)

    def save_preset_from_side(self, side: str, preset_name: str) -> tuple[bool, str | None]:
        config = self.baseline_config if side == "baseline" else self.candidate_config
        current_state = self.baseline_state if side == "baseline" else self.candidate_state
        target_path = self.preset_root / f"{preset_name}.yaml"
        allowed, message = can_overwrite_preset(target_path)
        if not allowed:
            return False, message
        metadata = dict(current_state.metadata)
        metadata.update(
            {
                "role": side,
                "origin": "user",
                "label": preset_name,
                "family": progression_family_label(config.progression),
            }
        )
        metadata.setdefault("description", f"user saved {side} preset")
        metadata.setdefault("recommended_cases", [])
        preset = ComparisonPreset(
            preset_name=preset_name,
            field_config=config,
            note=current_state.note,
            metadata=metadata,
        )
        save_preset(preset, target_path)
        self.set_side_from_preset(side, preset, source_path=target_path, unsaved=False)
        return True, None

    def copy_side(self, source: str, target: str) -> None:
        source_config = self.baseline_config if source == "baseline" else self.candidate_config
        source_state = self.baseline_state if source == "baseline" else self.candidate_state
        metadata = dict(source_state.metadata)
        metadata["role"] = target
        metadata["origin"] = "user"
        metadata["label"] = source_state.preset_name
        metadata["description"] = f"copied from {source}"
        preset = ComparisonPreset(
            preset_name=source_state.preset_name,
            field_config=source_config,
            note=source_state.note,
            metadata=metadata,
        )
        self.set_side_from_preset(target, preset, source_path=None, unsaved=True)

    def indexed_presets(self):
        return indexed_presets(self.preset_root)

    def grouped_preset_descriptors(self) -> tuple[list, list]:
        descriptors = indexed_presets(self.preset_root)
        baseline_descriptors = [descriptor for descriptor in descriptors if descriptor.role in (None, "baseline")]
        candidate_descriptors = [descriptor for descriptor in descriptors if descriptor.role in (None, "candidate")]
        return baseline_descriptors, candidate_descriptors

    def current_baseline_preset(self) -> ComparisonPreset:
        return self.baseline_state.to_preset(self.baseline_config, side="baseline")

    def current_candidate_preset(self) -> ComparisonPreset:
        return self.candidate_state.to_preset(self.candidate_config, side="candidate")
