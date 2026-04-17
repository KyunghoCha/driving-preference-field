# Parameter Catalog

This is the single lookup page for parameter exposure in Parameter Lab. It lists what is currently exposed, what is parameterizable but intentionally secondary, and what remains internal.

## Main

The `Main` surface contains the progression knobs that directly shape semantics the user is expected to read first.

- `longitudinal_frame`
- `longitudinal_family`
- `longitudinal_gain`
- `lookahead_scale`
- `longitudinal_shape`
- `transverse_family`
- `transverse_scale`
- `transverse_shape`
- `support_ceiling`

These are exposed in the right-side `Parameters` panel and persist in presets/config.

## Advanced

The `Advanced Surface` section contains research knobs that are parameterizable and now exposed, but intentionally behind a collapsed section by default.

- discretization
  - `anchor_spacing_m`
  - `spline_sample_density_m`
  - `spline_min_subdivisions`
  - `end_extension_m`
- support kernel
  - `min_sigma_t`
  - `min_sigma_n`
  - `sigma_t_scale`
  - `sigma_n_scale`
- modulation
  - `support_base`
  - `support_range`
  - `alignment_base`
  - `alignment_range`

These are useful for morphology quality, discretization locality, and weak modulation behavior, but they are not the first controls a user should reach for.

## View / tool candidates

View-only controls such as overlay visibility, scale normalization, interpolation style, or export presentation are real knobs, but they are tool-surface knobs rather than field-semantics knobs. They are not part of the current `Advanced Surface` section in this batch.

## Internal

Low-level numerical guards and implementation safety values remain internal. Examples include epsilon-style numerical guards such as `_EPS` and cache or batch constants. These should not be exposed as GUI controls.

## Current baseline

For the policy behind this split, read [Parameter Exposure Policy](../explanation/parameter_exposure_policy.md).
