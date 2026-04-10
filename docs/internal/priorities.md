# Internal Priorities

Roadmap phase tracking lives in `docs/status/roadmap_ko.md`.

## P0: Keep Phase 4 results stable

- keep Phase 4 complete docs, runtime contract, and lab behavior aligned
- avoid semantic drift between newcomer docs, status docs, and current implementation notes
- keep this repo as the score-field SSOT rather than an integration-specific branch

## P1: Preserve repeatable morphology experiments

- keep Parameter Lab useful for repeatable comparison, export, and profile inspection
- keep preset/config comparison as the primary experiment unit
- retune morphology only when downstream evidence shows a real need

## P2: Keep runtime query semantics stable

- keep `FieldRuntime` semantics aligned with evaluator semantics
- keep downstream consumers on the runtime API rather than formula copies
- treat cache and debug tooling as implementation detail, not separate truth

## P3: Prepare Phase 5 without promoting it early

- keep Phase 5 adapter thinking in reading/proposal docs only
- do not promote source-specific assumptions into canonical design docs
- keep SSC and other downstream systems as validation sources, not canonical truth

## P4: Keep adapters, planners, and geometry editing later

- do not pull source adapter work ahead of field/code alignment
- keep planner / Gazebo / RViz / MPPI integration out of this repo
- keep geometry editing out of the current phase
- treat interactive studio as a later phase built on top of a cleaned-up lab
