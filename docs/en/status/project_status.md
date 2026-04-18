# Project Status

This page is the current project snapshot. It is shorter than the roadmap and more concrete than the explanation docs.

## Completed

- progression-centered canonical docs and contracts
- Parameter Lab compare/export workflow
- progression-only base composition
- multiple progression-guide split/merge semantics
- advanced surface tuning controls in the GUI
- bilingual doc tree and UI language switching

## Current agreement

The active base score is `progression_tilted`. Drivable boundaries are read as overlay/support. Obstacle, rule, and dynamic channels stay in separate costmap-style layers. The project remains source-agnostic and keeps SSC as validation evidence rather than canonical truth.
The exact runtime remains the canonical evaluator. `planner_lookup` exists on `main` only as an internal acceleration backend for planner-facing experiments and Parameter Lab compare surfaces. It is not the public runtime contract.

## Current focus

- keep docs, UI help, and runtime aligned
- keep morphology experiments stable
- preserve the generic source-adapter contract while accepting explicit progression, global plan, or bounded drivable-only reconstruction at the raw adapter boundary

## Phase 4 acceptance

Parameter Lab is expected to remain a comparison and inspection tool, not a geometry editor or a downstream planner.

## Out of scope

Gazebo, RViz, MPPI coupling, and richer road-scene authoring remain outside the current status boundary. Internal acceleration infrastructure can exist on `main`, but downstream planner hookup is not promoted into the public project contract by that fact alone.
