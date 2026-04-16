from pathlib import Path

from driving_preference_field.config import ComparisonPreset, FieldConfig, SurfaceTuningConfig
from driving_preference_field.presets import (
    can_overwrite_preset,
    default_preset_path,
    indexed_presets,
    load_preset,
    presets_for_role,
    save_preset,
)


ROOT = Path(__file__).resolve().parents[1]
PRESET_ROOT = ROOT / "presets/lab"


def test_reference_preset_pack_is_loadable_and_has_standard_metadata() -> None:
    expected = {
        "baseline__no_progression",
        "baseline__weak_longitudinal",
        "baseline__balanced_field",
        "candidate__strong_longitudinal",
        "candidate__nonlinear_longitudinal",
        "candidate__inverse_transverse",
        "candidate__wide_transverse",
    }
    found = {path.stem for path in PRESET_ROOT.glob("*.yaml")}

    assert expected.issubset(found)

    for preset_name in expected:
        preset = load_preset(PRESET_ROOT / f"{preset_name}.yaml")
        assert {"role", "origin", "label", "family", "description", "recommended_cases"}.issubset(
            set(preset.metadata)
        )
        assert preset.field_config.progression.longitudinal_frame in {"local_absolute", "ego_relative"}
        assert preset.field_config.surface_tuning == SurfaceTuningConfig()


def test_role_filtered_preset_index_separates_reference_presets() -> None:
    baseline_names = {descriptor.path.stem for descriptor in presets_for_role("baseline", PRESET_ROOT)}
    candidate_names = {descriptor.path.stem for descriptor in presets_for_role("candidate", PRESET_ROOT)}

    assert "baseline__balanced_field" in baseline_names
    assert "candidate__strong_longitudinal" in candidate_names
    assert "candidate__strong_longitudinal" not in baseline_names
    assert "baseline__balanced_field" not in candidate_names


def test_default_preset_paths_point_to_reference_defaults() -> None:
    baseline_path = default_preset_path("baseline", PRESET_ROOT)
    candidate_path = default_preset_path("candidate", PRESET_ROOT)

    assert baseline_path is not None
    assert baseline_path.stem == "baseline__balanced_field"
    assert candidate_path is not None
    assert candidate_path.stem == "candidate__strong_longitudinal"


def test_reference_preset_cannot_be_overwritten() -> None:
    reference_path = PRESET_ROOT / "baseline__balanced_field.yaml"
    allowed, message = can_overwrite_preset(reference_path)

    assert allowed is False
    assert message is not None


def test_indexed_presets_include_reference_flags() -> None:
    descriptors = indexed_presets(PRESET_ROOT)
    names = {descriptor.path.stem: descriptor for descriptor in descriptors}

    assert names["baseline__balanced_field"].is_reference is True
    assert names["candidate__strong_longitudinal"].origin == "reference"


def test_saved_preset_roundtrip_preserves_surface_tuning(tmp_path) -> None:
    path = tmp_path / "advanced_surface.yaml"
    preset = ComparisonPreset(
        preset_name="advanced_surface",
        field_config=FieldConfig(
            surface_tuning=SurfaceTuningConfig(
                anchor_spacing_m=0.3,
                spline_min_subdivisions=16,
                transverse_handoff_temperature=0.08,
            )
        ),
        metadata={"role": "baseline"},
    )

    saved = save_preset(preset, path)
    loaded = load_preset(saved)

    assert loaded == preset
