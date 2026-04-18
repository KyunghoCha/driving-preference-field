<a id="parameter-lab-guide"></a>
# Parameter Lab Guide

This guide is the fastest way to get oriented inside Parameter Lab. It answers three practical questions: what the tool is for, where to start, and how to read the current views without mixing semantics and rendering artifacts.

Parameter Lab is not a geometry editor. It is an inspection tool for comparing field morphology over the same semantic snapshot and the same effective local context, then exporting that comparison as a reusable bundle.

<a id="what-this-tool-is-for"></a>
## What this tool is for

- compare `Baseline` and `Candidate` over the same case
- read `progression_tilted` and debug channels on a shared local map
- inspect split, merge, bend, and multilane behavior without changing the input geometry
- export a comparison bundle that can be reopened and reviewed later

<a id="start-here"></a>
## Start here

Start with this order:

1. Open a case and keep the same case on both sides.
2. Read `progression_tilted` on `Fixed` scale.
3. Change one item in `Main`, press `Apply`, and verify the result in `Diff`.

Use `Guide` when the question is “what should I do on this screen?” Use `Parameter Help` when the question is “what does this control change?”

<a id="quick-actions"></a>
## Quick actions

The shortest path to a useful comparison is:

1. `conda activate driving-preference-field`
2. From the repo root, run `PYTHONPATH=src python -m driving_preference_field parameter-lab`
3. Pick a case.
4. Pick baseline and candidate presets.
5. Keep `progression_tilted` on `Fixed` scale.
6. Change one parameter and press `Apply`.
7. Confirm the sign in `Diff`, then use `Export Comparison`.

Default shortcuts:

- `F5`: Reload Case
- `Ctrl+Shift+E`: Export Comparison
- `Ctrl+0`: Reset View
- `F1`: Guide

<a id="how-to-read-the-screen"></a>
## How to read the screen

<a id="top-toolbar"></a>
### Top toolbar

The top toolbar only keeps the actions you need often.

- `Reload Case`: reload the current case and rerun the comparison
- `Export Comparison`: export the current baseline/candidate bundle
- `Reset View`: reset pan and zoom on the current canvases
- `channel`: choose the raster channel to display
- `scale`: choose how the color range is interpreted
- `language`: switch the app, `Guide`, and `Parameter Help` between English and Korean
- `Guide`: open this guide inside the app

`Planner Lookup Progression Tilted` and `Planner Lookup Error` are internal compare channels. They visualize the internal planner lookup surrogate against the exact raster. They are not canonical runtime channels.

<a id="workspace"></a>
### Workspace

The left `Workspace` dock is for reading outputs.

- `Presets`: load, save, and copy baseline/candidate presets
- `Summary`: inspect the current comparison snapshot
- `Profile`: inspect line cuts and preview plots
- `Layers`: toggle overlay visibility

Use the left side to read. Use the right side to change parameters.

<a id="parameters"></a>
### Parameters

The right `Parameters` dock is the control area.

- `Main`: start here when you are interpreting field semantics directly
- `Advanced Surface`: open only when you are tuning morphology quality, discretization, support kernels, or modulation

The rule is simple: lock semantics with `Main` first, then open `Advanced Surface` only if a quality issue still remains.

<a id="canvas-views"></a>
### Canvas views

The raster is a sampled view of the continuous field, not the field contract itself.

- `Single`: read one side in isolation
- `Compare`: inspect morphology side by side
- `Diff`: read `candidate - baseline`

The cyan progression guide overlay is the raw input polyline, not the field itself. If `sensor_patch_open` looks slightly tilted, that is input truth, not a rendering bug.
If you select a planner lookup channel, read it as an internal acceleration comparison surface. The exact runtime channels remain the canonical inspection surface.

<a id="common-tasks"></a>
## Common tasks

<a id="compare-baseline-and-candidate"></a>
### Compare `Baseline` and `Candidate`

1. Keep the same case.
2. Select the baseline and candidate presets.
3. Read `progression_tilted` on `Fixed` scale.
4. Use `Compare` for morphology.
5. Use `Diff` for sign and magnitude.
6. Use `Profile` if you need a line cut.

<a id="change-one-parameter"></a>
### Change one parameter

1. Change one control in the right-side `Parameters` panel.
2. Press `Apply` to commit the staged edit.
3. Use `Reset` to discard the pending edit.

Case changes, case-control apply/reset, preset load, and baseline/candidate copy can trigger recomputation immediately. Parameter controls use a staged-edit flow.

<a id="read-split-merge-and-bend-cases"></a>
### Read split, merge, and bend cases

- split and merge are expressed with multiple progression guides
- the heatmap and the guide overlay do not need to share the same literal shape
- split or merge artifacts can come from either input semantics or tuning
- separate those two before treating a shape as a bug

<a id="read-profiles"></a>
### Read profiles

The `Profile` tab is an inspection surface, not a tuning surface. It shows baseline, candidate, and diff as both line-cut data and preview plots. If a preview image is larger than the viewport, scroll it.

<a id="export"></a>
## Export

`Export Comparison` keeps at least:

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

Export is therefore not just a screenshot. It is a comparison bundle that can be reviewed later.
The app asks for confirmation before it writes the export bundle, because export has file-system side effects and can take a moment.

<a id="limits"></a>
## Limits

Parameter Lab does not currently cover:

- geometry editing
- progression guide editing
- region drawing or editing
- source adapter implementation itself
- Gazebo / RViz / MPPI integration
- studio canvas authoring
- interactive drawing
- full 3D preview tooling

It stays focused on inspecting and comparing whole-space field morphology over a local map.

<a id="read-next"></a>
## Read next

- [Parameter Exposure Policy](../explanation/parameter_exposure_policy.md)
- [Parameter Catalog](../reference/parameter_catalog.md)
- [Project Overview](../explanation/project_overview.md)
- [Base Field Foundation](../explanation/base_field_foundation.md)
