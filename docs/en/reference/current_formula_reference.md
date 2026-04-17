# Current Formula Reference

This document records the current implementation math. It does not define the canonical philosophy by itself. Its job is to let a reader reconstruct what the current runtime is computing right now.

## How to read this document

Use this page when you need the active formula and current implementation shape, not when you need the higher-level design intent. For design intent, read [Base Field Foundation](../explanation/base_field_foundation.md).

## Common notation

The runtime evaluates guide-local blended coordinates and a guide-local score, then takes a hard max envelope across progression guides. Higher values are better.

## Progression surface

### Guide-local anchor coordinates

Each progression guide is resampled into anchors. The current implementation uses Gaussian anchor blending to estimate local guide coordinates such as `s_hat`, `n_hat`, and the local tangent.

### Guide-local Gaussian weights

Anchor weights stay local to a guide. They shape support and local coordinate estimation, and they are normalized within the guide-local computation.

### Guide-local coordinate

The runtime derives `s_hat`, `n_hat`, and a local tangent from the guide-local anchor blend. These coordinates define the longitudinal and transverse reading for that guide.

### Guide-local longitudinal frame

The longitudinal frame can be interpreted as `local_absolute` or `ego_relative`, depending on configuration. The exact longitudinal component is computed from that guide-local frame.

### Longitudinal families

The runtime supports several longitudinal families such as `tanh`, `linear`, `inverse`, and `power`, all controlled by the active configuration.

### Transverse families

The runtime supports several transverse families such as `exponential`, `inverse`, and `power`. The exported transverse channel is the dominant guide's actual transverse term; it is not a separate smoothed inspection channel.

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
