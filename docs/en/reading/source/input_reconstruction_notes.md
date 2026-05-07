# Input Reconstruction Notes

> This is a non-canonical reading note. The active contracts live in [Input Semantics](../../reference/input_semantics.md) and [Source Adapter](../../reference/source_adapter.md).

## 1. Semantic Support Conditions

### Facts already fixed in canonical docs

Progression support is the main base-field input. Drivable support is domain/support input rather than base additive ordering. Branches are represented with multiple progression guides.

### Information confirmed in discussion

Current toy and generic fixtures have been cleaned up to match the progression-guide-only semantics for split and merge.

### Items not promoted into fixed truth yet

Richer road semantics, intersections, roundabouts, and more complex source shapes remain deferred until they are intentionally promoted.

## 2. Input capability tiers

### Tier 1. Sensor-only local input

Minimal local support with limited structure.

### Tier 2. Map-assisted input

Adds stronger progression/drivable structure without requiring a full HD-map semantics stack.

### Tier 3. Rich structured input

Adds richer lane, rule, and scene semantics, but is still upstream of canonical truth.

## 3. SSC mapping example

SSC remains a useful validation source for mapping downstream scene information into the generic adapter contract.

## 4. Deferred scenario questions

Intersections and roundabouts remain research topics, not fixed adapter truth.

## 5. Current surface quality notes

Split/merge and bend morphology observations are still useful reading material, but the canonical runtime contract lives elsewhere.
