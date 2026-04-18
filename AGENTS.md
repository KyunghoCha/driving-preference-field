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
- when branch/split morphology work creates or revises a baseline, record it with a stable sequence label such as `B7`, the exact commit hash, and the commit timestamp under `docs/raw/notes/`, and put the same number in the approved baseline-promotion commit subject as `[B7]`; use baseline numbers only for behavior-changing surface baselines, not for docs-only or workflow-only commits
- when an approved baseline or an important baseline-adjacent workflow correction lands, update the relevant `docs/raw/notes/` entry in the same batch rather than deferring it; keep a running baseline ledger there
- in that raw baseline ledger, accumulate approved baselines with hash + one-line meaning, and mention failed/intermediate experiments only briefly as context instead of preserving a full failed-experiment changelog
- separate refactors from behavior changes
- move docs with current truth
- record intent, baseline, hypothesis, non-goals, and verification boundaries with the change
- review for stale residue, unused knobs, dead formula paths, and docs/code mismatch
- if a task proposes changes to `AGENTS.md`, skills, operating docs, experiment workflow docs, or user-facing semantics, first review terminology consistency, evidence and rationale, factual accuracy, clarity, overlap or contradiction risk, and overall rationality, then discuss the proposal and get approval before mutating those surfaces
- if a user proposes a repo-level intuition, heuristic, role definition, or workflow thought, discuss it first and, once approved, capture the user's original messages under `docs/raw/notes/`, preserve enough surrounding user context to resolve referential fragments, then update `docs/raw/owner_thought_tracker.md`, then `docs/raw/owner_design_history.md`, and only after that update `docs/raw/owner_design_notebook.md` when the latest design framing changes before translating the idea into canonical docs
- if the user explicitly designates the current active thread as the authoritative source for those notes, prefer the current thread and any confirmed materialized cluster over speculative historical `.codex` archaeology
- if the user explicitly designates a broader materialized source window, reread that source set before expanding summaries, widen `docs/raw/notes/` first, and only then update derived docs
- if a user plan message (`PLEASE IMPLEMENT THIS PLAN` or similar) is what actually locks a design transition, it may be used as a raw anchor alongside the surrounding user discussion
- treat `docs/raw/owner_design_notebook.md` as raw-grounded clean design prose, not as a free-standing interpretation layer
- treat `docs/raw/owner_design_history.md` as raw-grounded clean design history prose, not as a latest-design summary
- treat no-touch or out-of-scope boundaries as batch-local defaults, not permanent law; if better evidence appears, update the boundary explicitly with the change
- when code has non-obvious intent or a deliberate tradeoff, capture that intent in naming, a short comment, or a docstring; do not add comments that only restate obvious code

For Codex-specific routing, also see the repo-local skill under [`plugins/dpf-working-rules/`](./plugins/dpf-working-rules/).
