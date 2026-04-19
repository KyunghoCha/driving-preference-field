import numpy as np

from driving_preference_field.visualization_scale import (
    SCALE_MODE_FIXED,
    SCALE_MODE_NORMALIZED,
    display_unit,
    format_display_range,
    resolve_display_range,
)


def test_fixed_range_uses_channel_contract() -> None:
    data = np.array([[0.1, 0.4], [0.7, 1.1]], dtype=float)

    value_range = resolve_display_range(
        data,
        channel_name="progression_tilted",
        scale_mode=SCALE_MODE_FIXED,
    )

    assert value_range == (0.0, 5.0)


def test_normalized_range_uses_observed_data() -> None:
    data = np.array([[0.2, 0.4], [0.7, 1.1]], dtype=float)

    value_range = resolve_display_range(
        data,
        channel_name="progression_tilted",
        scale_mode=SCALE_MODE_NORMALIZED,
    )

    assert value_range == (0.2, 1.1)


def test_fixed_diff_range_is_symmetric() -> None:
    data = np.array([[-0.3, 0.1], [0.7, -1.2]], dtype=float)

    value_range = resolve_display_range(
        data,
        channel_name="progression_tilted",
        scale_mode=SCALE_MODE_FIXED,
        diff=True,
    )

    assert value_range == (-5.0, 5.0)


def test_display_range_text_includes_mode_and_unit() -> None:
    text = format_display_range(
        "safety_soft",
        scale_mode=SCALE_MODE_FIXED,
        value_range=(0.0, 2.0),
    )

    assert "fixed" in text
    assert "cost score" in text
    assert display_unit("safety_soft", diff=True) == "cost delta"


def test_longitudinal_component_fixed_range_matches_linear_shape_ceiling() -> None:
    data = np.array([[0.2, 1.7], [2.8, 3.4]], dtype=float)

    value_range = resolve_display_range(
        data,
        channel_name="progression_longitudinal_component",
        scale_mode=SCALE_MODE_FIXED,
    )

    assert value_range == (0.0, 8.0)


def test_transverse_component_fixed_range_matches_peak_ceiling() -> None:
    data = np.array([[0.2, 1.7], [2.8, 3.4]], dtype=float)

    value_range = resolve_display_range(
        data,
        channel_name="progression_transverse_term",
        scale_mode=SCALE_MODE_FIXED,
    )

    assert value_range == (0.0, 4.0)
