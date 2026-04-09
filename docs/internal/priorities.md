# Internal Priorities

Roadmap phase tracking lives in `docs/status/roadmap_ko.md`.

## P0: Tune canonical field morphology

- validate whether the current longitudinal/transverse coupling produces the intended field shape
- use Parameter Lab to compare morphology inside one canonical model
- keep the main question on field shape, not UI polish

## P1: Align Parameter Lab with canonical parameter axes

- expose longitudinal, transverse, and support/gate axes more directly
- keep the lab useful for repeatable comparison while reducing semantic drift
- preserve fixed-scale interpretability

## P2: Preserve repeatable experiments

- keep evaluator re-runnable on the same semantic snapshot with different configs
- keep presets as the unit of repeatable comparison
- keep export bundles sufficient for reproduction

## P3: Keep non-compensatory composition stable

- separate base field from obstacle/rule/dynamic layers
- avoid quietly falling back to naive addition
- define a prototype ordering rule for hard, soft, and base outputs

## P4: Keep adapters and geometry editing later

- do not pull source adapter work ahead of field/code alignment
- keep geometry editing out of the current phase
- treat interactive studio as a later phase built on top of a cleaned-up lab
