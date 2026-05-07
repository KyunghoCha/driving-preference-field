# Current Formula Reference

This document records the current implementation math. It does not define the canonical philosophy by itself. Its job is to let a reader reconstruct what the current runtime is computing right now.

## How to read this document

Use this page when you need the active formula and current implementation shape, not when you need the higher-level design intent. For design intent, read [Reference-Path Cost Model Foundation](../explanation/base_field_foundation.md).

## Common notation

The runtime evaluates guide-local blended progress coordinates and a guide-local score, then takes a hard max envelope across progression guides. The per-guide transverse distance is read as shortest distance to the raw visible progression guide polyline. Higher values are better.

## Progression surface

### Guide-local anchor coordinates

Each progression guide is resampled into anchors. The current implementation uses Gaussian anchor blending to estimate local progress coordinates such as `s_hat` and the local tangent. The transverse distance is read separately from the raw visible progression guide geometry.

### Guide-local Gaussian weights

Anchor weights stay local to a guide. They shape support, progress coordinate estimation, and the local tangent, and they are normalized within the guide-local computation.

### Guide-local coordinate

The runtime derives `s_hat` and a local tangent from the guide-local anchor blend. For the same dominant guide, `center_distance` is then read as shortest distance to that guide's raw visible polyline.

`s_hat = sum_i \bar{w}_i s_i`

`t_hat = normalize(sum_i \bar{w}_i t_i)`

`center_distance = min_{q \in C_g} ||p - q||`

where `C_g` is the raw visible polyline for guide `g`.

### Guide-local longitudinal frame

The longitudinal frame can be interpreted as `local_absolute` or `ego_relative`, depending on configuration. The exact longitudinal component is computed from that guide-local frame.

### Longitudinal families

The runtime supports several longitudinal families such as `tanh`, `linear`, `inverse`, and `power`, all controlled by the active configuration. In the current implementation, `longitudinal_peak` sets the function-space ceiling directly before gain is applied. In the `linear` family, `longitudinal_shape` still scales the ramp slope and therefore also the endpoint ceiling.

### Transverse families

The runtime supports several transverse families such as `exponential`, `inverse`, `power`, and `linear`. Each guide's transverse term is built directly from the shortest unsigned distance in meters to that guide's raw visible polyline. In the current implementation, `transverse_peak` sets the center ceiling directly, `transverse_shape` controls the core profile near the center, and `transverse_falloff` adds extra outer-tail suppression. The exported `progression_transverse_term` can therefore exceed `1.0` through `transverse_peak`. The old user-facing transverse-width knob is no longer part of the active runtime contract.

### Secondary modulation

Support modulation and alignment modulation remain weak secondary factors. They shape the result without replacing the main progression-centered ordering.

### Final progression score

The active progression score is:

`progression_tilted(p) = max_g support_mod_g * alignment_mod_g * (T(center_distance_g) + gain * L(u_g))`

The score merge is a hard max envelope across progression guides.

## Exception layers

Obstacle, rule, and dynamic signals are not part of the base progression formula. They remain separate cost-like or burden-style layers.

## Current tiny evaluator composition

The current tiny evaluator treats `progression_tilted` as the main base score and keeps obstacle / rule / dynamic costs separate from the reference-path cost model contract.
