from dataclasses import fields
from pathlib import Path

from driving_preference_field.config import ProgressionConfig, SurfaceTuningConfig
from driving_preference_field.ui.help.catalog import ADVANCED_PARAMETER_GROUPS, MAIN_PARAMETER_KEYS, PARAMETER_ORDER, PARAMETER_SPECS


ROOT = Path(__file__).resolve().parents[1]


def test_parameter_catalog_covers_progression_and_surface_tuning_fields() -> None:
    progression_keys = {field.name for field in fields(ProgressionConfig)}
    surface_keys = {field.name for field in fields(SurfaceTuningConfig)}

    assert set(MAIN_PARAMETER_KEYS) == progression_keys
    assert {key for key, spec in PARAMETER_SPECS.items() if spec.config_namespace == "progression"} == progression_keys
    assert {key for key, spec in PARAMETER_SPECS.items() if spec.config_namespace == "surface_tuning"} == surface_keys
    assert set(PARAMETER_ORDER) == progression_keys | surface_keys


def test_parameter_catalog_metadata_is_complete() -> None:
    advanced_keys = {key for _, keys in ADVANCED_PARAMETER_GROUPS for key in keys}
    for key, spec in PARAMETER_SPECS.items():
        assert spec.label
        assert spec.section_key
        assert spec.tier in {"main", "advanced"}
        assert spec.widget_kind in {"combo", "double_spin", "spin"}
        assert spec.practical_band
        assert spec.technical_range
        if spec.widget_kind == "combo":
            assert spec.options
        else:
            assert spec.numeric_range is not None
        if spec.tier == "main":
            assert key in MAIN_PARAMETER_KEYS
        else:
            assert key in advanced_keys


def test_parameter_help_shims_are_thin_compatibility_modules() -> None:
    parameter_lab_window = ROOT / "src/driving_preference_field/ui/parameter_lab_window.py"
    parameter_guide = ROOT / "src/driving_preference_field/ui/parameter_guide.py"

    assert "from driving_preference_field.ui.parameter_lab.window import ParameterLabWindow" in parameter_lab_window.read_text(
        encoding="utf-8"
    )
    guide_text = parameter_guide.read_text(encoding="utf-8")
    assert "from driving_preference_field.ui.help.catalog import" in guide_text
    assert "from driving_preference_field.ui.help.render import" in guide_text
