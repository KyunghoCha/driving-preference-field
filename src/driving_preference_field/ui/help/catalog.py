from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParameterSpec:
    key: str
    label: str
    section_key: str
    config_namespace: str
    tier: str
    widget_kind: str
    practical_band: str
    technical_range: str
    options: tuple[str, ...] = ()
    numeric_range: tuple[float, float] | None = None
    decimals: int = 4
    single_step: float = 0.05
    minimum_width: int = 120


MAIN_PARAMETER_KEYS: tuple[str, ...] = (
    "longitudinal_frame",
    "longitudinal_family",
    "longitudinal_gain",
    "lookahead_scale",
    "longitudinal_shape",
    "transverse_family",
    "transverse_scale",
    "transverse_shape",
    "support_ceiling",
)


ADVANCED_PARAMETER_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "discretization",
        (
            "anchor_spacing_m",
            "spline_sample_density_m",
            "spline_min_subdivisions",
            "end_extension_m",
        ),
    ),
    (
        "support_kernel",
        (
            "min_sigma_t",
            "min_sigma_n",
            "sigma_t_scale",
            "sigma_n_scale",
        ),
    ),
    (
        "modulation",
        (
            "support_base",
            "support_range",
            "alignment_base",
            "alignment_range",
        ),
    ),
)


ADVANCED_PARAMETER_RANGES: dict[str, tuple[float, float]] = {
    "anchor_spacing_m": (0.05, 2.0),
    "spline_sample_density_m": (0.01, 1.0),
    "spline_min_subdivisions": (1, 64),
    "min_sigma_t": (0.05, 5.0),
    "min_sigma_n": (0.05, 5.0),
    "sigma_t_scale": (0.05, 5.0),
    "sigma_n_scale": (0.05, 5.0),
    "end_extension_m": (0.0, 10.0),
    "support_base": (0.0, 1.0),
    "support_range": (0.0, 1.0),
    "alignment_base": (0.0, 1.0),
    "alignment_range": (0.0, 1.0),
}


PARAMETER_SPECS: dict[str, ParameterSpec] = {
    "longitudinal_frame": ParameterSpec(
        key="longitudinal_frame",
        label="frame",
        section_key="longitudinal",
        config_namespace="progression",
        tier="main",
        widget_kind="combo",
        practical_band="local_absolute | ego_relative",
        technical_range="local_absolute | ego_relative",
        options=("local_absolute", "ego_relative"),
    ),
    "longitudinal_family": ParameterSpec(
        key="longitudinal_family",
        label="long family",
        section_key="longitudinal",
        config_namespace="progression",
        tier="main",
        widget_kind="combo",
        practical_band="tanh | linear | inverse | power",
        technical_range="tanh | linear | inverse | power",
        options=("tanh", "linear", "inverse", "power"),
    ),
    "longitudinal_gain": ParameterSpec(
        key="longitudinal_gain",
        label="long gain",
        section_key="longitudinal",
        config_namespace="progression",
        tier="main",
        widget_kind="double_spin",
        practical_band="0.5 .. 3.0",
        technical_range="0.0 .. 1000.0",
        numeric_range=(0.0, 1000.0),
    ),
    "lookahead_scale": ParameterSpec(
        key="lookahead_scale",
        label="long horizon",
        section_key="longitudinal",
        config_namespace="progression",
        tier="main",
        widget_kind="double_spin",
        practical_band="0.1 .. 1.0",
        technical_range="0.0 .. 1000.0",
        numeric_range=(0.0, 1000.0),
    ),
    "longitudinal_shape": ParameterSpec(
        key="longitudinal_shape",
        label="long shape",
        section_key="longitudinal",
        config_namespace="progression",
        tier="main",
        widget_kind="double_spin",
        practical_band="0.5 .. 4.0",
        technical_range="0.0 .. 1000.0",
        numeric_range=(0.0, 1000.0),
    ),
    "transverse_family": ParameterSpec(
        key="transverse_family",
        label="trans family",
        section_key="transverse",
        config_namespace="progression",
        tier="main",
        widget_kind="combo",
        practical_band="exponential | inverse | power",
        technical_range="exponential | inverse | power",
        options=("exponential", "inverse", "power"),
    ),
    "transverse_scale": ParameterSpec(
        key="transverse_scale",
        label="trans scale",
        section_key="transverse",
        config_namespace="progression",
        tier="main",
        widget_kind="double_spin",
        practical_band="0.25 .. 3.0",
        technical_range="0.0 .. 1000.0",
        numeric_range=(0.0, 1000.0),
    ),
    "transverse_shape": ParameterSpec(
        key="transverse_shape",
        label="trans shape",
        section_key="transverse",
        config_namespace="progression",
        tier="main",
        widget_kind="double_spin",
        practical_band="0.5 .. 4.0",
        technical_range="0.0 .. 1000.0",
        numeric_range=(0.0, 1000.0),
    ),
    "support_ceiling": ParameterSpec(
        key="support_ceiling",
        label="support cap",
        section_key="support_gate",
        config_namespace="progression",
        tier="main",
        widget_kind="double_spin",
        practical_band="0.25 .. 1.0",
        technical_range="0.0 .. 1000.0",
        numeric_range=(0.0, 1000.0),
    ),
    "anchor_spacing_m": ParameterSpec(
        key="anchor_spacing_m",
        label="anchor spacing",
        section_key="discretization",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.05 .. 2.0",
        technical_range="0.05 .. 2.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["anchor_spacing_m"],
    ),
    "spline_sample_density_m": ParameterSpec(
        key="spline_sample_density_m",
        label="spline density",
        section_key="discretization",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.01 .. 1.0",
        technical_range="0.01 .. 1.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["spline_sample_density_m"],
    ),
    "spline_min_subdivisions": ParameterSpec(
        key="spline_min_subdivisions",
        label="min subdivisions",
        section_key="discretization",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="spin",
        practical_band="1 .. 64",
        technical_range="1 .. 64",
        numeric_range=ADVANCED_PARAMETER_RANGES["spline_min_subdivisions"],
        decimals=0,
        single_step=1.0,
    ),
    "end_extension_m": ParameterSpec(
        key="end_extension_m",
        label="end extension",
        section_key="discretization",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.0 .. 10.0",
        technical_range="0.0 .. 10.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["end_extension_m"],
    ),
    "min_sigma_t": ParameterSpec(
        key="min_sigma_t",
        label="min sigma_t",
        section_key="support_kernel",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["min_sigma_t"],
    ),
    "min_sigma_n": ParameterSpec(
        key="min_sigma_n",
        label="min sigma_n",
        section_key="support_kernel",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["min_sigma_n"],
    ),
    "sigma_t_scale": ParameterSpec(
        key="sigma_t_scale",
        label="sigma_t scale",
        section_key="support_kernel",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["sigma_t_scale"],
    ),
    "sigma_n_scale": ParameterSpec(
        key="sigma_n_scale",
        label="sigma_n scale",
        section_key="support_kernel",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["sigma_n_scale"],
    ),
    "support_base": ParameterSpec(
        key="support_base",
        label="support base",
        section_key="modulation",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["support_base"],
        single_step=0.01,
    ),
    "support_range": ParameterSpec(
        key="support_range",
        label="support range",
        section_key="modulation",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["support_range"],
        single_step=0.01,
    ),
    "alignment_base": ParameterSpec(
        key="alignment_base",
        label="alignment base",
        section_key="modulation",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["alignment_base"],
        single_step=0.01,
    ),
    "alignment_range": ParameterSpec(
        key="alignment_range",
        label="alignment range",
        section_key="modulation",
        config_namespace="surface_tuning",
        tier="advanced",
        widget_kind="double_spin",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        numeric_range=ADVANCED_PARAMETER_RANGES["alignment_range"],
        single_step=0.01,
    ),
}


PARAMETER_ORDER: tuple[str, ...] = (
    *MAIN_PARAMETER_KEYS,
    *(key for _, keys in ADVANCED_PARAMETER_GROUPS for key in keys),
)


def parameter_spec(key: str) -> ParameterSpec:
    return PARAMETER_SPECS[key]
