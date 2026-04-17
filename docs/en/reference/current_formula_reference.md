# Current Formula Reference

This document records the active implementation math. It does not define canonical philosophy by itself. Its job is to let a reader reconstruct what the runtime is computing right now.

## How to read this document

Use this page when you need the active formula and current implementation shape, not when you need the higher-level design intent. For design intent, read [Base Field Foundation](../explanation/base_field_foundation.md).

## Common notation

The runtime now evaluates one pooled blended coordinate field across the full progression anchor pool. Higher values are better.

## Progression surface

### Guide-local anchor coordinates

Each progression guide is still resampled into anchors, but the runtime no longer closes the field by picking one guide winner first. The active evaluator reads all progression anchors as one pooled control structure.

### Guide-local Gaussian weights

The first pass computes Gaussian raw weights across the whole anchor pool:

`raw0_i = guide_weight_i * confidence_i * exp(-0.5 * ((tau_i / sigma_t_i)^2 + (nu_i / sigma_n)^2))`

The runtime normalizes `raw0` once to estimate a provisional pooled progress coordinate `s_hat0`.

### Guide-local coordinate

After the provisional progress estimate, the runtime applies one extra soft progress gate:

`progress_gate_i = exp(-0.5 * ((s_i - s_hat0) / sigma_t_i)^2)`

`raw_i = raw0_i * progress_gate_i`

The final pooled coordinates are then computed from normalized `raw_i`.

### Guide-local longitudinal frame

The longitudinal frame is interpreted from the pooled coordinate field, not from a pointwise guide winner. In `local_absolute`, the runtime blends guide extents into pooled `s_min_hat` and `s_max_hat`. In `ego_relative`, the runtime first evaluates the pooled field at the ego pose to get `ego_s_hat`, then normalizes forward progress within the pooled lookahead span.

### Longitudinal families

The runtime supports `tanh`, `linear`, `inverse`, and `power`, all controlled by the active configuration. These families shape the pooled longitudinal component `L(u)`.

### Transverse families

The runtime supports `exponential`, `inverse`, and `power`. The main score uses the pooled lateral reading `T(|n_hat|)`. The exported `progression_transverse_component` remains an inspection channel: it uses guide-aware smoothing across eligible guides so split/merge inspection does not collapse to one guide contribution too early.

### Secondary modulation

Support modulation and alignment modulation remain weak secondary factors. They shape the result without replacing the main progression-centered ordering.

### Final progression score

The active pooled score is:

`progression_tilted(p) = support_mod * alignment_mod * (T(|n_hat|) + gain * L(u))`

There is no hard max envelope across progression guides in the current implementation.

## Exception layers

Obstacle, rule, and dynamic signals are not part of the base progression formula. They remain separate cost-like or burden-style layers.

## Current tiny evaluator composition

The current tiny evaluator still treats `progression_tilted` as the main base score and keeps obstacle / rule / dynamic costs separate from the base field contract.
