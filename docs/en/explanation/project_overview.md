# Project Overview

This document explains why `driving-preference-field` exists, what it is trying to build, and where the project stands today. The first question it fixes is simple: is this repo a tool for picking a discrete path, or a tool for defining a preference structure over the whole visible local map?

This project works on a whole-space preference field rather than a path scorer. Instead of telling the system to follow one line, it defines an ordering over states and trajectories in the current local map. The field does not choose an action directly. It gives an optimizer or downstream layer a preference landscape that makes natural motion easier to recover.

A single reference path is not enough to explain good driving flow. The nearest center or the most direct continuation is not always the most natural trajectory. If a planner is supposed to make good local decisions, it needs a preference structure over the full local space before it chooses one discrete route.

That is why this repo centers progression semantics. Progression is not just heading. It describes what counts as before and after in this local place, and which continuations are compatible with intended forward flow. Drivable semantics answer a different question: where motion is currently allowed.

Progression and drivable meaning should not be collapsed into one bonus score. Drivable support alone does not tell the system what is before or after. Progression alone does not guarantee where motion is currently possible. This repo therefore treats progression as the main source of preference, while drivable support is read as domain, support, and reconstruction input.

The same split determines how branch structure and obstacles are handled. Branches are not something the field should resolve into a winner in advance. It is more consistent with the project’s intent to read them as multiple valid continuations inside progression support. Obstacles, rules, and dynamic actors are not the same kind of object as the ideal base preference, so they live in separate layers instead of being merged into the base score.

The current runtime moves in that direction. The main base score is read from `progression_tilted`. Drivable boundaries are handled as overlay and support. Obstacle, rule, and dynamic actor signals are separated into costmap-style visualization and burden layers. The implementation tries to stay aligned with the canonical philosophy without pretending that every current detail is itself canonical.

SSC is an important downstream validation source for this idea. It matters because it shows whether the field abstraction is useful in a real consumer. But SSC is not the canonical truth. This repo keeps the source-agnostic field and contract as the reference point, and treats SSC-derived observations as evidence rather than doctrine.

The current project state is `Phase 5 complete, Phase 6 preparation`. Canonical docs and contracts are in place, the toy evaluator and local raster visualization are working, Parameter Lab compare/export flows exist, the cached runtime query layer is in place, and the source adapter contract has been stabilized. `planner_lookup` also exists on `main` as an internal acceleration backend for planner-facing experiments and compare surfaces, but the exact runtime remains canonical. Gazebo, RViz, MPPI, and optimizer integration are still outside the repo’s core public scope.

In one sentence, `driving-preference-field` defines a progression-centered whole-space preference field over the visible local map and makes that ordering available to downstream optimizers and evaluation tooling.
