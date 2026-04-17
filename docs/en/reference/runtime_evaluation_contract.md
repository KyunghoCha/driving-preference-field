# Runtime Evaluation Contract

This document defines the public runtime contract for evaluating the field. It fixes what the runtime exposes and what downstream consumers are allowed to rely on.

## Definition

The runtime evaluates a progression-centered whole-space preference field over the visible local map. The sign convention is `higher is better`.

## Field semantics

The field is a whole-space preference field, not a route selector. It exposes an ordering over states and trajectories. Downstream optimizers or evaluators can consume that ordering, but they should not assume the field has already selected a unique winner direction.

## Public runtime interface

The public interface is centered on `FieldRuntime` query methods such as `FieldRuntime.query_state(state)` and the corresponding trajectory/grid helpers. The runtime returns the active base score and associated current-implementation detail channels that remain part of the public contract.

## Runtime evaluation

The runtime evaluates the active progression field under the current `FieldConfig`, snapshot, and query context. It is allowed to cache implementation detail for speed, but the semantic meaning of the returned score should stay stable under the contract.

## Properties that must hold

- `higher is better`
- the base field remains progression-centered
- hard max envelope semantics remain part of the current implementation unless the docs and code move together
- base-field meaning stays distinct from obstacle/rule/dynamic cost-like layers

## Layer-wise evaluator contract

The runtime can expose current-implementation detail channels such as longitudinal, transverse, support modulation, and alignment modulation. These are inspection channels, not separate canonical layers.

## Current implementation

The current implementation builds guide-local coordinates and scores from progression guides, then takes a pointwise hard max envelope across guides. `progression_transverse_component` includes handoff smoothing for inspection quality. Obstacle / rule / dynamic channels remain separate cost-like views.

## Visualization

Visualization is a sampled view of the continuous runtime field over the local map. The raster image is not the contract by itself. It is one inspection surface over the contract.

## Relation to optimizers

The runtime provides the field ordering. An optimizer or consumer decides how to turn that ordering into actual motion. Optimizer policy is therefore downstream of this contract.

## Current baseline

For the exact active formula, see [Current Formula Reference](./current_formula_reference.md).
