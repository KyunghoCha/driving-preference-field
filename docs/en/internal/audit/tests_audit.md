# Tests Audit

## Current role

This audit records the shape of tracked regression tests.

## Current state

The test suite covers runtime behavior, docs integrity, GUI flows, loaders, and CI-sensitive launcher behavior.

## Problem types

### 1. Docs tests can overfit exact wording

The suite should prefer structural and truth checks over brittle prose matching.

### 2. Large GUI tests are expensive

UI tests need to stay focused on behavior that matters.

### 3. Audit expectations can lag behind structure changes

Docs tree changes require parity and link checks, not legacy path assumptions.

## Keep

Cross-language docs parity checks and Parameter Lab smoke coverage.

## Change

Prefer tests that lock semantics and structure over tests that freeze incidental phrasing.

## Defer

Do not try to encode every reading-note sentence into regression tests.

## Next rewrite order

1. docs parity and link tests
2. UI language-switch tests
3. runtime/preset persistence tests
