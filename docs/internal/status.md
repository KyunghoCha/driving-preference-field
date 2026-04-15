# Internal Status

- 역할: internal
- 현재성: non-canonical
- 대상 독자: maintainer
- 다음으로 읽을 문서: [internal priorities](./priorities.md)

Date: 2026-04-08

## Project State

- canonical docs and code now align on a single source-agnostic progression field
- Phase 5 is complete and the repo is in Phase 6 prep state
- tiny evaluator, toy cases, generic adapter fixtures, raster visualization, cached runtime queries, and a Parameter Lab GUI exist
- this repo remains the score-field SSOT, not an integration workspace

## Current Truth

The project is not currently implementing:

- a planner
- a controller
- a full MPPI stack
- an interactive geometry editor
- Gazebo / RViz hookup

The project is currently defining:

- what the base field is
- how a local-map-wide progression-aware field is described
- how longitudinal and transverse terms are treated as independent axes
- how support, confidence, continuity, and alignment remain secondary modulation
- how exception layers remain separate
- how runtime local evaluation should be interpreted
- how config-driven comparison and preset-based experiments should work in the implemented lab
- how newcomer-facing docs explain the current truth without promoting downstream specifics to canonical status
- how a generic external-like source is translated into the canonical snapshot/context contract

## Current Focus

- keep Phase 5 results stable as SSOT
- treat morphology retuning as downstream-evidence-driven, not as open-ended redesign
- keep the fixed adapter contract in design SSOT and the proposal history in reading docs
- prevent SSC or any other downstream environment from becoming canonical truth by accident

## Cleanup Boundary

- canonical docs and code are aligned on the single-field naming
- old experimental naming has been removed from active code, presets, and tests
- remaining work is about SSOT stability, docs clarity, and later downstream preparation, not version cleanup
