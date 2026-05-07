# Input Semantics

This reference fixes the canonical semantic slots expected by the field. Its job is not to explain why each slot exists in detail. Its job is to define the minimum meaning an upstream source must provide before the runtime can evaluate a field.

## Definition

The canonical input is built around `SemanticInputSnapshot + QueryContext`. The snapshot carries semantic support for the field. The query context carries the effective ego pose, local window, and evaluation mode.

## Required semantic slots

### 1. Progression support

Progression support provides the guide structure that defines intended forward flow over the local map. This is the main base-field input. Split and merge are represented with multiple progression guides rather than a separate branch-guide layer.

### 2. Drivable support

Drivable support provides the currently movable domain and related geometry support. It is not the base additive preference itself. It is used as domain, support, and reconstruction input.

## Optional semantic slots

### 3. Boundary / interior support

Boundary or interior support can be provided when the source knows useful geometry priors. These are optional supports rather than mandatory canonical slots.

### 4. Exception-layer support

Obstacle, rule, and dynamic-layer support live outside the reference-path cost model. They can be provided as separate exception or burden-style inputs, but they are not the same semantic layer as the progression-centered base score.

## Partial input

Partial input is acceptable as long as the adapter makes the absence explicit. The contract does not require every source to provide the same richness. It requires the adapter to preserve meaning and avoid inventing canonical claims that the source did not actually provide.

## Out of scope

The canonical input does not directly choose a branch winner, planner policy, or control action. It also does not require a full HD map or a scene editor. Those concerns are outside this reference unless they become part of the active contract later.

## Current implementation

The current implementation still evaluates canonical progression support through coherent progression guides. At the generic adapter boundary, those guides may come from explicit `progression_supports`, normalized `global_plan_supports`, or bounded drivable-only reconstruction for corridor-like single-continuation local geometry.

When raw progression-like inputs are obviously fragmented into a single forward chain, the adapter may normalize them into one canonical guide before runtime evaluation. This is normal adapter behavior for global-plan and drivable-derived progression. For explicit fragmented `progression_supports`, it is only a best-effort fallback over upstream-owned input, and the adapter records normalization provenance and severity in snapshot metadata instead of silently upgrading that input shape into a first-class canonical semantics.

Drivable boundaries are kept as overlay/support input, and obstacle/rule/dynamic signals stay in separate cost-like layers.

## Current baseline

The active source-adapter output contract is documented in [Source Adapter](./source_adapter.md). The current runtime behavior that consumes these inputs is documented in [Runtime Evaluation Contract](./runtime_evaluation_contract.md).
