# Experiment Plan

This page records the current morphology comparison workflow for the repo.

## Current phase

The repo is in `Phase 5 complete, Phase 6 preparation`.

## Current experiment targets

- progression morphology under different main settings
- split / merge / bend behavior
- advanced-surface tuning effects

## Comparison procedure

1. keep the same case and local context
2. compare baseline and candidate on `progression_tilted`
3. inspect `Diff`
4. inspect `Profile` when needed
5. export the comparison bundle

## Experiment axes

### Longitudinal

Frame, family, gain, horizon, and shape.

### Transverse

Family, scale, shape, and handoff behavior.

### Support / confidence / continuity

Secondary morphology tuning through support, alignment, discretization, and kernel settings.

## Baseline and candidate

Baseline and candidate should be kept structurally comparable. The point is to isolate one meaningful difference at a time.

## Common cases

Use straight, bend, split, merge, and open/sensor-patch style cases as the default inspection set.

## Outputs

Each useful comparison should leave behind presets, summary payloads, profile results, and exported images where needed.

## Late Phase 4 semantic acceptance

The tool should still be able to explain why a visible difference happened rather than only show that a difference exists.

## Current focus

Use advanced surface tuning deliberately and keep semantic interpretation ahead of visual preference.

## Out of scope

This experiment plan does not define simulator evaluation or control-loop policy.

## Deferred scenarios

Intersections, roundabouts, and richer road semantics remain deferred research topics.
