# Research Scope

This document fixes what the repo currently claims, and what it does not claim yet. It is not a roadmap and not a marketing page. Its job is to keep the research boundary clear enough that implementation detail, downstream success, and future ambitions do not silently expand the scope.

The current scope is a progression-centered whole-space preference field over the visible local map. That includes the base field concept, the split between progression semantics and drivable semantics, the runtime contract for evaluating states and trajectories, and the tooling needed to inspect morphology and compare parameter settings.

The scope also includes a generic source-adapter contract. The repo is allowed to define how a source should provide progression support, drivable support, optional layer support, and query context. It is not required to bind that contract to one downstream system.

Parameter Lab, local raster visualization, profile inspection, preset comparison, and export flows are inside scope because they help inspect and validate the field itself. These tools are not downstream planners. They are analysis and iteration surfaces for the field abstraction.

What is outside the current scope is equally important. The repo does not currently claim to solve planner integration, closed-loop control, Gazebo or RViz hookup, or production-level optimizer coupling. It also does not claim to provide a full semantic map editor or a complete road-scene authoring studio.

Intersections, roundabouts, and richer road semantics remain active research questions, not fixed claims. They can appear in notes, backlog, or experimental cases, but they should not be treated as settled canonical behavior until the docs and implementation move together.

The current project state is `Phase 5 complete, Phase 6 preparation`. That means the repo has a stable enough canonical layer, toy/runtime layer, and adapter contract to support the next phase of experimentation, but it is still intentionally short of downstream deployment scope.
