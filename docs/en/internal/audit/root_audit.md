# Root and Supporting Files Audit

## Audit scope

This page covers root-level tracked files, launcher assets, and supporting configuration surfaces.

## Current role

Root files define the repo landing page, environment contract, CI behavior, and launcher entry points.

## Current state

README, bilingual docs portals, environment pinning, launchers, and CI smoke checks are in place.

## Problem types

### 1. CI strictness

Platform coverage should increase only when the runs are stable enough to trust.

### 2. Root surface vs docs portal

The root should stay a landing page, not a second full manual.

### 3. Launcher surface still depends on environment assumptions

Launchers are only as stable as the environment contract they rely on.

### 4. Asset quality can drift

Icons, desktop entries, and launcher docs need occasional review.

## Keep

The thin root landing page and explicit environment contract.

## Change

Continue reducing hardcoded paths and platform surprises.

## Defer

Do not turn the root into a packaging or installer system before the repo needs it.
