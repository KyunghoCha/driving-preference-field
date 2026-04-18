# Internal Status

## Project state

Phase 5 is complete and the repo is in Phase 6 preparation.

## Current truth

The repo is progression-centered, bilingual docs are active, and Parameter Lab is the main morphology comparison tool.
The exact runtime remains the canonical behavior surface.
`planner_lookup` is now present on `main`, but only as an internal planner-facing surrogate for acceleration experiments. It is exact-oracle-based, position-only, and reuse-oriented. It does not replace the exact runtime contract.

## Current focus

- keep docs and runtime aligned
- keep comparison tooling stable
- keep the planner lookup/backend boundary explicit
- avoid widening downstream scope too early

## Cleanup boundary

Internal cleanup should not silently change public semantics.
