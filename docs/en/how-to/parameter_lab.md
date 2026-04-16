# Parameter Lab Guide

This guide explains how to use Parameter Lab in practice. It answers three questions: what the tool is for, how to compare baseline and candidate settings, and how to read the heatmaps, guides, and profiles on screen.

Parameter Lab is not a geometry editing studio. It is a research tool for comparing field morphology over the same semantic snapshot and the same effective local context, then exporting that comparison in a reusable bundle.

## When to read this guide

- when you open the app for the first time and need a starting point
- when you are not sure whether to begin with `Single`, `Compare`, `Diff`, or `Profile`
- when you want to understand the difference between `Guide` and `Parameter Help`
- when you need to know what presets, channels, scale, and export actually do

## Quick start

1. `conda activate driving-preference-field`
2. From the repo root, run `PYTHONPATH=src python -m driving_preference_field parameter-lab`
3. Pick a case.
4. Pick baseline and candidate presets.
5. Start with `progression_tilted` on `Fixed` scale.
6. Change one item in the right-side `Parameters` panel and press `Apply`.
7. Verify the result in `Diff` and `Profile`, then use `Export Comparison`.

In practice, changing one variable at a time is the safest way to read results. If case, ego pose, preset, and parameter all move together, the cause of the difference becomes hard to recover.

## How to read the screen

### Top toolbar

The top toolbar only keeps the actions you use frequently.

- `Reload Case`
  - reload the current case and rerun the comparison
- `Export Comparison`
  - export the current baseline/candidate comparison, preset snapshots, and profile outputs
- `Reset View`
  - reset pan and zoom on the current canvases
- `channel`
  - choose the channel to display
- `scale`
  - choose how colors should be interpreted
- `language`
  - switch the whole app, the guide, and the parameter help between English and Korean
- `Guide`
  - open this guide inside the app

Default shortcuts:

- `F5`: Reload Case
- `Ctrl+Shift+E`: Export Comparison
- `Ctrl+0`: Reset View
- `F1`: Guide

### Left workspace

The left `Workspace` dock is the reading area.

- `Presets`
  - load, save, and copy baseline/candidate presets
- `Summary`
  - inspect the current comparison snapshot
- `Profile`
  - inspect line cuts and profile preview images
- `Layers`
  - toggle overlay visibility

The left side is for reading outputs. The right side is for changing parameters.

### Right parameters panel

The right `Parameters` dock is the control area.

- `Main`
  - the first controls to use when you are interpreting field semantics directly
- `Advanced Surface`
  - research tuning knobs for morphology quality, discretization, support kernels, modulation, and handoff smoothing

The rule is simple: use `Main` to understand semantic meaning first, then open `Advanced Surface` only when a quality issue remains.

## What to look at first

### 1. `progression_tilted`

Always start with `progression_tilted`. It is the current representative base score. The canonical sign is `higher is better`.

### 2. `Fixed` scale

Start with `Fixed` scale. Baseline and candidate then share the same color-to-value mapping, which makes comparison easier. `Normalized` is a secondary exploration mode.

### 3. `Diff`

`Diff` always means `candidate - baseline`. Positive means candidate is higher. Negative means baseline is higher.

### 4. Guide overlays

The cyan progression guide overlay is the raw input polyline, not the field itself. For example, if `sensor_patch_open` looks slightly tilted, that is not a rendering bug. The case input literally defines the guide as `[-0.5, 0.0] -> [2.5, 0.15]`.

## Common tasks

### Compare baseline and candidate

1. Keep the same case.
2. Select the baseline and candidate presets.
3. Read `progression_tilted` on `Fixed` scale.
4. Use `Compare` to inspect morphology.
5. Use `Diff` to inspect sign and magnitude.
6. Use `Profile` if you need a line cut.

### Change one parameter

1. Change one control in the right-side `Parameters` panel.
2. The result does not update immediately.
3. Press `Apply` to commit the staged edit.
4. Use `Reset` if you want to discard pending edits.

Case changes, case-control apply/reset, preset load, and baseline/candidate copy can trigger recomputation immediately. Parameter controls use a staged-edit flow.

### Read split, merge, and bend cases

- split and merge are represented with multiple progression guides
- the raster view is a sampled image of a continuous local field
- the guide overlay and the heatmap do not need to share the same literal shape
- before treating a shape as a bug, separate input semantics from tuning artifacts

### Read profiles

The `Profile` tab is an inspection surface, not a tuning surface. It shows baseline, candidate, and diff as both line-cut data and preview plots. If a preview image is larger than the viewport, use scrolling.

## Guide vs Parameter Help

The two help surfaces answer different questions.

- `Guide`
  - where to start, what to look at, and how to use the tool step by step
- `Parameter Help`
  - what each parameter in the right-side panel changes

If your question is “what should I do on this screen?”, use `Guide`. If your question is “what happens when I raise this value?”, use `Parameter Help`.

## What export contains

The comparison export keeps at least:

- the case path
- the selected channel
- the effective ego pose
- the effective local window
- baseline and candidate preset snapshots
- summary metrics
- profile summary
- the qualitative note

Profile inspection export includes:

- `profile_baseline.png`
- `profile_candidate.png`
- `profile_diff.png`
- `profile_data.json`

Export is therefore not just a screenshot. It is a bundle that can reconstruct the comparison later.

## Current implementation scope

Parameter Lab currently includes:

- case selection
- direct opening of generic adapter input paths
- case-level ego/window control
- baseline and candidate parameter panels
- single / compare / diff views
- preset save / load / copy
- summary metrics
- qualitative notes
- comparison export
- fixed / normalized scale modes
- `progression_tilted` as the default selected channel
- profile inspection
- debug channels such as `s_hat`, `n_hat`, longitudinal/transverse/support/alignment components

The GUI does not expose every canonical concept, but it does expose both `Main` controls for reading `progression_tilted` and `Advanced Surface` controls for tuning current implementation morphology. Drivable boundaries are read as overlays. Obstacle / rule / dynamic channels remain costmap-like overlays rather than base score channels.

## Current limits

Parameter Lab is not currently responsible for:

- geometry editing
- progression guide editing
- region drawing or editing
- source adapter implementation itself
- Gazebo / RViz / MPPI integration
- studio canvas authoring
- interactive drawing
- full 3D preview tooling

The GUI raster is only a sampled view of a continuous field over the local map. Parameter Lab remains an inspection and comparison tool for whole-space field morphology rather than a downstream integration tool.

## Read next

- [Parameter Exposure Policy](../explanation/parameter_exposure_policy.md)
- [Parameter Catalog](../reference/parameter_catalog.md)
- [Project Overview](../explanation/project_overview.md)
- [Base Field Foundation](../explanation/base_field_foundation.md)
