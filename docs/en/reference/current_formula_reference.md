# Current Formula Reference

This document records the current implementation math. It does not define the canonical philosophy by itself. Its job is to let a reader reconstruct what the current runtime is computing right now.

## How to read this document

Use this page when you need the active formula and current implementation shape, not when you need the higher-level design intent. For design intent, read [Base Field Foundation](../explanation/base_field_foundation.md).

## Common notation

The runtime evaluates one pooled blended coordinate field across all progression anchors. Higher values are better.

## Progression surface

### Anchor coordinates

Each progression guide is resampled into anchors. The current implementation uses Gaussian anchor blending over the full anchor pool to estimate `s_hat`, `n_hat`, and the pooled tangent.

### Pooled Gaussian weights

Anchor weights are computed across the full pool. A provisional pooled `s_hat0` is used to apply soft progress gating before the final normalized blend is formed.

### Pooled coordinate

The runtime derives `s_hat`, `n_hat`, and a pooled tangent from the final normalized blend. These coordinates define the longitudinal and transverse reading used by the exported channels and the score.

### Longitudinal frame

The longitudinal frame can be interpreted as `local_absolute` or `ego_relative`, depending on configuration. The exact longitudinal component is computed from the pooled coordinate field.

### Longitudinal families

The runtime supports several longitudinal families such as `tanh`, `linear`, `inverse`, and `power`, all controlled by the active configuration.

### Transverse families

The runtime supports several transverse families such as `exponential`, `inverse`, and `power`. The exported `progression_transverse_component` is the exact pooled transverse term that also goes into the score.

### Secondary modulation

Support modulation and alignment modulation remain weak secondary factors. They shape the result without replacing the main progression-centered ordering.

### Final progression score

The active progression score is:

`progression_tilted(p) = support_mod * alignment_mod * (T(|n_hat|) + gain * L(u))`

There is no guide-local hard max envelope in the current implementation. Guide diagnostics such as dominant guides are derived from pooled raw contribution only.

## Exception layers

Obstacle, rule, and dynamic signals are not part of the base progression formula. They remain separate cost-like or burden-style layers.

## Current tiny evaluator composition

The current tiny evaluator treats `progression_tilted` as the main base score and keeps obstacle / rule / dynamic costs separate from the base field contract.
