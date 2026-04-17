# DPF Agent Entry Point

Use this file as the repo-local starting point for AI-assisted work in `driving-preference-field`.

Before changing code, formulas, tests, docs, or experiment workflow, read:

1. [`docs/en/explanation/engineering_operating_principles.md`](./docs/en/explanation/engineering_operating_principles.md)
2. [`docs/en/status/experiment_plan.md`](./docs/en/status/experiment_plan.md)
3. [`docs/en/explanation/documentation_writing_principles.md`](./docs/en/explanation/documentation_writing_principles.md) when the task changes docs, help copy, or other user-facing text

Default working discipline:

- start from a clean baseline
- keep one meaningful hypothesis per branch or worktree
- separate refactors from behavior changes
- move docs with current truth
- record baseline, hypothesis, and verification boundaries with the change
- review for stale residue, unused knobs, dead formula paths, and docs/code mismatch

For Codex-specific routing, also see the repo-local skill under [`plugins/dpf-working-rules/`](./plugins/dpf-working-rules/).
