# driving-preference-field

[한국어 README](./README.ko.md)

[![ci](https://github.com/KyunghoCha/driving-preference-field/actions/workflows/ci.yml/badge.svg)](https://github.com/KyunghoCha/driving-preference-field/actions/workflows/ci.yml)

`driving-preference-field` is a research workspace for defining and testing a whole-space driving preference field over the visible local map. Current state: `Phase 5 complete, Phase 6 preparation`.

## What This Repo Is For

- keep the canonical progression-centered field semantics and runtime contract stable
- run repeatable morphology experiments in Parameter Lab
- keep the source-adapter contract generic enough for downstream consumers

This repo is not currently responsible for planner integration, Gazebo/RViz hookup, or full downstream control loops.

## Prerequisites

- Python/conda environment defined in [environment.yml](./environment.yml)
- Recommended environment name: `driving-preference-field`
- Current known-good NumPy version: `1.26.4`

## Quick Start

1. `conda env create -f environment.yml`
2. `conda activate driving-preference-field`
3. `PYTHONPATH=src python -m driving_preference_field parameter-lab`

## Docs

- Language landing page: [docs/index.md](./docs/index.md)
- English portal: [docs/en/index.md](./docs/en/index.md)
- Korean portal: [docs/ko/index.md](./docs/ko/index.md)

Recommended newcomer reading order:

1. [Project Overview](./docs/en/explanation/project_overview.md)
2. [Engineering Operating Principles](./docs/en/explanation/engineering_operating_principles.md)
3. [Base Field Foundation](./docs/en/explanation/base_field_foundation.md)
4. [Source Adapter](./docs/en/reference/source_adapter.md)
5. [Runtime Evaluation Contract](./docs/en/reference/runtime_evaluation_contract.md)
6. [Roadmap](./docs/en/status/roadmap.md)

## Parameter Lab

Parameter Lab is the main experiment UI for comparing baseline and candidate progression settings over the same local map sample. It supports English/Korean UI switching from the top toolbar and opens the matching `Guide` and `Parameter Help` content from `docs/en` or `docs/ko`.

## Current Scope

- canonical docs and contracts
- progression-surface morphology experiments
- presets, exports, and comparison tooling
- source-agnostic semantic input loading

## References

- Current formula reference: [docs/en/reference/current_formula_reference.md](./docs/en/reference/current_formula_reference.md)
- External references log: [docs/en/reading/references/external_references.md](./docs/en/reading/references/external_references.md)
