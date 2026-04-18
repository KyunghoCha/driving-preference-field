# Source Adapter

This reference defines what the source adapter is responsible for producing. The adapter is a semantic translator. It does not choose actions, finalize planner policy, or redefine canonical meaning around one downstream source.

## Responsibility

The source adapter translates source-specific scene information into the repo’s canonical `SemanticInputSnapshot + QueryContext` contract. Its job is to preserve semantic meaning while keeping the result generic enough for multiple upstream providers and downstream consumers.

## Canonical output

### SemanticInputSnapshot

The snapshot carries the semantic supports that the field itself consumes. Progression support is the main base-field input. Drivable support carries domain and geometry support. Optional layer supports can exist without being promoted into the base field.

### QueryContext

The query context carries the effective ego pose, local window, and evaluation mode. These values shape how the runtime is queried. They are not themselves the base field meaning.

## Generic reference input schema

The generic adapter schema exists to show one source-agnostic way to serialize these semantic slots. It is not the only allowed source shape, but it is the reference path for externalization and fixtures.

## Required and optional inputs

Drivable support and query context are the minimum raw inputs. Progression support may arrive in three forms, with this precedence:

1. explicit `progression_supports`
2. `global_plan_supports`
3. drivable-only reconstruction from `drivable_regions`

Boundary or interior priors, support/confidence metadata, and exception-layer signals are optional and should stay explicitly optional in adapter output.

## Separation that must be preserved

The adapter must preserve the split between progression and drivable meaning. It must not silently collapse branch semantics into a preselected winner, and it must not quietly promote obstacle or rule layers into the base progression score.

## Relation to toy inputs

Toy YAML cases and generic adapter fixtures both feed the same canonical snapshot/context contract. Toy inputs exist to keep experiments small. They do not replace the adapter contract.

## Inspection path

The adapter should make it possible to inspect what semantic supports were reconstructed, rather than only returning a finished black-box bundle. Inspection and debugging are part of the intended workflow.

## Relation to SSC

SSC is an important downstream validation source, but SSC-specific structure is not canonical by itself. The adapter may map SSC into the canonical slots, but the repo still treats the generic snapshot/context contract as the stable reference.

## Current implementation

The current runtime still consumes the same canonical output slots: progression support, drivable support, optional boundary/interior support, and optional exception layers. At the generic adapter boundary, progression may now be provided explicitly, normalized from a global plan, or reconstructed from drivable-only corridor-like local geometry.

Current normalization policy is intentionally asymmetric:

- `global_plan_supports` and drivable-only reconstruction are normal adapter inputs, so obvious single-chain fragmentation may be normalized into one canonical guide without special escalation.
- explicit `progression_supports` are still treated as upstream responsibility, but the adapter now applies a best-effort fallback for obvious single-chain fragmentation and records that fallback in snapshot metadata.
- ambiguous split/merge-like continuation is not guessed silently; the adapter leaves the input unmerged and records warning/error-style normalization metadata instead.

## Current baseline

When in doubt, treat `SemanticInputSnapshot + QueryContext` as the single active adapter output contract.
