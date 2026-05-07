# Runtime Evaluation Contract

This document defines the public runtime contract for evaluating the field. It fixes what the runtime exposes and what downstream consumers are allowed to rely on.

## Definition

The runtime evaluates a progression-centered local reference path cost surface over the visible local map. The sign convention is `higher is better`.

## Field semantics

The field is a local reference path cost surface, not a route selector. It exposes an ordering over states and trajectories. Downstream optimizers or evaluators can consume that ordering, but they should not assume the field has already selected a unique winner direction.

## Public runtime interface

The public interface is centered on `FieldRuntime` query methods such as `FieldRuntime.query_state(state)` and the corresponding trajectory/grid helpers. The runtime returns the active base score and associated current-implementation detail channels that remain part of the public contract.

## Runtime evaluation

The runtime evaluates the active progression field under the current `FieldConfig`, snapshot, and query context. It is allowed to cache implementation detail for speed, but the semantic meaning of the returned score should stay stable under the contract.

## Properties that must hold

- `higher is better`
- the reference-path cost model remains progression-centered
- hard max envelope semantics remain part of the current implementation unless the docs and code move together
- base-field meaning stays distinct from obstacle/rule/dynamic cost-like layers

## Layer-wise evaluator contract

The runtime can expose current-implementation detail channels such as longitudinal, transverse, support modulation, and alignment modulation. These are inspection channels, not separate canonical layers.

## Current implementation

The current implementation builds guide-local blended progress coordinates and scores from progression guides, reads each guide's transverse term from shortest distance to that guide's raw visible polyline, and then takes a pointwise hard max envelope across guides. Exported detail channels now match the dominant guide exactly:

- `progression_s_hat`: dominant guide blended progress coordinate
- `progression_center_distance`: dominant guide raw visible polyline distance
- `progression_transverse_term`: dominant guide score transverse term

Obstacle / rule / dynamic channels remain separate cost-like views.

## Visualization

Visualization is a sampled view of the continuous runtime field over the local map. The raster image is not the contract by itself. It is one inspection surface over the contract.

## Relation to optimizers

The runtime provides the field ordering. An optimizer or consumer decides how to turn that ordering into actual motion. Optimizer policy is therefore downstream of this contract.

For one concrete downstream example, see [SSC Pure-Field Consumption](./ssc_pure_field_consumption.md). That page is consumer-specific and does not redefine the base LRPC runtime contract.

## Current baseline

For the exact active formula, see [Current Formula Reference](./current_formula_reference.md).
