# DPF Agent Entry Point

Use this file as the repo-local starting point for AI-assisted work in `driving-preference-field`.

Before changing code, formulas, tests, docs, or experiment workflow, read:

1. [`docs/en/explanation/engineering_operating_principles.md`](./docs/en/explanation/engineering_operating_principles.md)
2. [`docs/en/status/experiment_plan.md`](./docs/en/status/experiment_plan.md)
3. [`docs/en/explanation/documentation_writing_principles.md`](./docs/en/explanation/documentation_writing_principles.md) when the task changes docs, help copy, or other user-facing text

Default working discipline:

- when network access is available, first study the relevant official docs or other strong external references before changing architecture, terminology, workflow, or user-facing behavior
- start from a clean baseline
- keep one meaningful hypothesis per branch or worktree
- separate refactors from behavior changes
- move docs with current truth
- record intent, baseline, hypothesis, non-goals, and verification boundaries with the change
- review for stale residue, unused knobs, dead formula paths, and docs/code mismatch
- if a task proposes changes to `AGENTS.md`, skills, operating docs, experiment workflow docs, or user-facing semantics, first review terminology consistency, evidence and rationale, factual accuracy, clarity, overlap or contradiction risk, and overall rationality, then discuss the proposal and get approval before mutating those surfaces
- if a user proposes a repo-level intuition, heuristic, role definition, or workflow thought, discuss it first and, once approved, capture the user's original messages under `docs/raw/notes/`, preserve enough surrounding user context to resolve referential fragments, update `docs/raw/owner_thought_tracker.md`, and update `docs/raw/owner_design_notebook.md` as clean design prose before translating the idea into canonical docs
- if the user explicitly designates the current active thread as the authoritative source for those notes, prefer the current thread and any confirmed materialized cluster over speculative historical `.codex` archaeology
- treat `docs/raw/owner_design_notebook.md` as raw-grounded clean design prose, not as a free-standing interpretation layer
- treat no-touch or out-of-scope boundaries as batch-local defaults, not permanent law; if better evidence appears, update the boundary explicitly with the change
- when code has non-obvious intent or a deliberate tradeoff, capture that intent in naming, a short comment, or a docstring; do not add comments that only restate obvious code

For Codex-specific routing, also see the repo-local skill under [`plugins/dpf-working-rules/`](./plugins/dpf-working-rules/).
