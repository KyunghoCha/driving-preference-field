---
name: dpf-working-rules
description: Use when a task changes code, docs, formulas, tests, or experiment workflow inside the driving-preference-field repo. First study the relevant external references when network access is available, then read the repo operating docs and define the clean baseline, hypothesis, and verification boundary before making changes.
---

# DPF Working Rules

Use this skill for work inside the `driving-preference-field` repository.

This skill is a router, not the source of truth. Keep it short. Read the repo docs below and follow them.

## Quick start

1. Read `docs/en/explanation/engineering_operating_principles.md`.
2. Read `docs/en/status/experiment_plan.md`.
3. If the task changes docs, help copy, or other user-facing text, also read `docs/en/explanation/documentation_writing_principles.md`.
4. When network access is available, review the relevant official docs or other strong external references before changing architecture, terminology, workflow, or user-facing behavior.
5. State the current intent, the clean baseline, the current hypothesis, the non-goals, and the verification boundary before making changes.

## Guardrails

- Start from a clean baseline.
- Keep one meaningful hypothesis per branch or worktree.
- Separate refactors from behavior changes.
- Move docs with current truth.
- Study external references first when the task needs terminology, workflow, UX/help, or architecture decisions.
- Review for stale residue, unused knobs, dead formula paths, and docs/code mismatch.
- If the task proposes changes to `AGENTS.md`, skills, operating docs, experiment workflow docs, or user-facing semantics, first review terminology consistency, evidence and rationale, factual accuracy, clarity, overlap or contradiction risk, and overall rationality, then discuss the proposal and get approval before mutating those surfaces.
- If a user proposes a repo-level intuition, heuristic, role definition, or workflow thought, discuss it first and, once approved, capture the user's original messages under `docs/raw/` before translating the idea into canonical docs.
- Treat no-touch or out-of-scope boundaries as batch-local defaults, not permanent law.
- When code has non-obvious intent or a deliberate tradeoff, capture that intent in naming, a short comment, or a docstring. Do not comment obvious code.

## Scope

Use this skill when the task touches any of:

- runtime or formula behavior
- tests or experiment acceptance
- repo docs or in-app help
- experiment execution workflow
- parameter exposure or interpretation

Do not copy the full operating principles or experiment plan into the skill. Those documents remain the SSOT.
