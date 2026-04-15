# Internal Priorities

- 역할: internal
- 현재성: non-canonical
- 대상 독자: maintainer
- 다음으로 읽을 문서: [internal glossary](./glossary.md)

Roadmap phase tracking lives in `docs/status/roadmap_ko.md`.

## P0: Keep Phase 5 results stable

- keep Phase 5 complete docs, runtime contract, adapter contract, and lab behavior aligned
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

## P3: Keep the adapter contract generic

- keep source adapter assumptions source-agnostic and generic
- do not promote source-specific assumptions into canonical design docs or contract types
- keep SSC and other downstream systems as validation sources, not canonical truth

## P4: Keep planners, geometry editing, and integration later

- keep planner / Gazebo / RViz / MPPI integration out of this repo
- keep geometry editing out of the current phase
- treat interactive studio as a later phase built on top of a cleaned-up lab
