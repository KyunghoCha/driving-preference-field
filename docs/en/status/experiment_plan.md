# Experiment Plan

This page records how the repo should run and record DPF comparison experiments. It is not only a morphology checklist. It is the working execution guide for keeping experiments comparable, explainable, and easy to discard or recombine.

## Current phase

The repo is in `Phase 5 complete, Phase 6 preparation`.

## Current experiment targets

- progression morphology under different main settings
- split / merge / bend behavior
- advanced-surface tuning effects

## What counts as a baseline

DPF experiments need more than one kind of baseline.

- `code baseline`: the clean commit, branch, or worktree that the experiment starts from
- `comparison baseline`: the preset/config/case bundle that the candidate is compared against
- `historical baseline`: an earlier known state used to check whether a newer direction actually improved the behavior
- `rollback baseline`: the clean state that the experiment can return to if the direction turns out to be wrong

In practice, a meaningful DPF baseline includes `commit + case + local context + preset`. A commit alone is not enough if the experiment changes case selection, query window, or preset shape.

## Recommended experiment isolation

Treat `main` as the clean reference baseline. Run one meaningful hypothesis per branch, and prefer a separate worktree when the experiment can interfere with other ongoing edits.

Do not mix refactors and behavior changes in the same experimental batch unless the refactor itself is the thing being validated. If you need both, separate them so you can explain what changed, what stayed fixed, and what should be rolled back if the result is wrong.

## Comparison procedure

1. Keep the same case and local context unless the experiment is explicitly about changing them.
2. Select the comparison baseline preset and the candidate preset.
3. Compare baseline and candidate on `progression_tilted` first.
4. Inspect `Diff`.
5. Inspect `Profile` when the spatial view is not enough to explain the change.
6. Export the comparison bundle when the difference is worth keeping.

## Experiment axes

### Longitudinal

Frame, family, gain, horizon, and shape.

### Transverse

Family, scale, shape, and handoff behavior.

### Support / confidence / continuity

Secondary morphology tuning through support, alignment, discretization, and kernel settings.

## How to record an experiment

The commit subject should say what changed. The commit body should say why the change exists, what it is trying to improve, and what it is not trying to change.

When the experiment needs durable comparison context, include structured metadata in the commit message body or trailers. Useful fields include:

- `Baseline`: the clean code baseline or reference commit
- `Compare-Against`: the baseline experiment or historical state being compared
- `Verification`: the tests, cases, exports, or visual checks used to validate the result

The point is not to force one rigid template. The point is to make the hypothesis, baseline, and verification boundary recoverable later.

## Verify, discard, and recombine

Before changing the code, decide what should improve and what must not regress. That usually means naming the acceptance cases, the regression surface, and the non-goals up front.

If the experiment improves one target but damages another important surface, do not keep layering patches on top of the same dirty state. Prefer discarding the failed direction, returning to the clean baseline, and starting the next attempt from there. If two directions both have value, recombine them deliberately from a clean baseline rather than by accident.

## What review should catch

Review should catch more than immediate correctness. In this repo, it should also look for:

- dead code
- dead formula paths
- unused knobs
- stale implementation residue from failed experiments
- docs/code mismatch
- unnecessary complexity or over-engineering

The goal is not perfection. The goal is to make sure each accepted change leaves the repo easier to understand and easier to compare than before.

## Common cases

Use straight, bend, split, merge, U-turn, and open/sensor-patch style cases as the default inspection set.

## Outputs

Each useful comparison should leave behind presets, summary payloads, profile results, and exported images where needed. The comparison should still be explainable after the original editing session is gone.

## Current focus

Use advanced surface tuning deliberately and keep semantic interpretation ahead of visual preference.

## Out of scope

This experiment plan does not define simulator evaluation or control-loop policy. It does not lock the repo to one permanent Git workflow either. It records the discipline that currently keeps experiments understandable and reproducible.

## Deferred scenarios

Intersections, roundabouts, and richer road semantics remain deferred research topics.
