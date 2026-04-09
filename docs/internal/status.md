# Internal Status

Date: 2026-04-08

## Project State

- canonical docs and code now align on a single source-agnostic progression field
- tiny evaluator, toy cases, raster visualization, and a Parameter Lab GUI exist
- the immediate focus is longitudinal/transverse morphology experiments inside Phase 4, not a source adapter

## Current Truth

The project is not currently implementing:

- a planner
- a controller
- a full MPPI stack
- a source adapter yet
- an interactive geometry editor

The project is currently defining:

- what the base field is
- how a local-map-wide progression-aware field is described
- how longitudinal and transverse terms are treated as independent axes
- how support, confidence, continuity, and alignment remain secondary modulation
- how exception layers remain separate
- how runtime local evaluation should be interpreted
- how config-driven comparison and preset-based experiments should work in the implemented lab

## Cleanup Boundary

- canonical docs and code are aligned on the single-field naming
- old experimental naming has been removed from active code, presets, and tests
- remaining work is about field morphology and parameter exposure, not version cleanup
