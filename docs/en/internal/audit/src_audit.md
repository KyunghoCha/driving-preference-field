# Src Audit

## Current role

This audit records the current shape of tracked source modules.

## Current state

The codebase is centered on contracts, runtime evaluation, progression-surface implementation, adapters, presets, rendering, and the Parameter Lab UI.

## Problem types

### 1. Public-facing text can drift

UI labels, docstrings, and help text need periodic consistency checks.

### 2. UI module coupling can grow

The Parameter Lab window remains the main coupling point and should stay under control.

### 3. Runtime wording can drift from docs

Source comments and public contracts need to move with docs.

### 4. Internal implementation details can leak outward

Advanced tuning and current implementation math should remain clearly marked when exposed.

## Keep

The progression-centered runtime contract and source-adapter split.

## Change

Reduce unnecessary text drift and keep locale/help surfaces consistent.

## Defer

Do not widen into planner integration.

## Next rewrite order

1. UI help strings
2. runtime-facing comments
3. adapter inspection text
