# Current Formula Reference

This document records the current implementation math. It does not define the canonical philosophy by itself. Its job is to let a reader reconstruct what the current runtime is computing right now.

## How to read this document

Use this page when you need the active formula and current implementation shape, not when you need the higher-level design intent. For design intent, read [Base Field Foundation](../explanation/base_field_foundation.md).

## Common notation

The runtime evaluates guide-local blended coordinates and a guide-local score, then takes a hard max envelope across progression guides. Higher values are better.

## Progression surface

### Guide-local anchor coordinates

Each progression guide is resampled into anchors. The current implementation uses Gaussian anchor blending to estimate local guide coordinates such as `s_hat`, `n_hat`, and the local tangent. Before those anchors are blended, the runtime first projects the query point onto the smoothed guide to get a local arclength reference `s_ref`.

### Guide-local Gaussian weights

Anchor weights stay local to a guide. They shape support and local coordinate estimation, and they are normalized within the guide-local computation. The current implementation now applies a soft arclength-locality gate around the projection-selected branch neighborhood instead of blending equally across the whole guide.

Projection-derived local arclength reference:

`s_ref = sum_k q_k * s_proj_k`

`q_k ∝ exp(-0.5 * d_k^2 / sigma_proj^2)`

Guide-local raw weight:

`r_i = w_i^guide * c_i * exp(-0.5 * ((tau_i / sigma_t)^2 + (nu_i / sigma_n)^2))`

Soft arclength-locality gate:

`g_i = exp(-0.5 * ((|s_i - s_ref| / sigma_s)^2))`

`r_i <- r_i * g_i`

### Guide-local coordinate

The runtime derives `s_hat`, `n_hat`, and a local tangent from the same softened guide-local anchor blend. These coordinates define the longitudinal and transverse reading for that guide, so the locality gate affects support, coordinates, and score together rather than mixing local coordinates with global support.

### Guide-local longitudinal frame

The longitudinal frame can be interpreted as `local_absolute` or `ego_relative`, depending on configuration. The exact longitudinal component is computed from that guide-local frame.

### Longitudinal families

The runtime supports several longitudinal families such as `tanh`, `linear`, `inverse`, and `power`, all controlled by the active configuration.

### Transverse families

The runtime supports several transverse families such as `exponential`, `inverse`, and `power`. The current implementation also applies transverse handoff smoothing across near-dominant guides for the exported transverse inspection channel.

### Secondary modulation

Support modulation and alignment modulation remain weak secondary factors. They shape the result without replacing the main progression-centered ordering.

### Final progression score

The active progression score is:

`progression_tilted(p) = max_g support_mod_g * alignment_mod_g * (T(|n_hat_g|) + gain * L(u_g))`

The score merge is a hard max envelope across progression guides.

## Exception layers

Obstacle, rule, and dynamic signals are not part of the base progression formula. They remain separate cost-like or burden-style layers.

## Current tiny evaluator composition

The current tiny evaluator treats `progression_tilted` as the main base score and keeps obstacle / rule / dynamic costs separate from the base field contract.
