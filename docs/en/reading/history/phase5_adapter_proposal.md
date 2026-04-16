# Phase 5 Adapter Proposal History

> This is proposal history. The active adapter contract lives in [Source Adapter](../../reference/source_adapter.md).

## Current proposal core

### 1. The adapter is only a semantic translator

It should not silently become a planner.

### 2. Progression and drivable are separate

They answer different questions and should stay separate in the contract.

### 3. Ego pose belongs closer to query context than snapshot meaning

It shapes evaluation rather than defining scene semantics by itself.

### 4. Local window policy remains experimental

It belongs to query/evaluation policy more than canonical semantic meaning.

### 5. The canonical contract does not choose a branch winner

Multiple valid continuations are allowed.

### 6. Support/confidence can stay weak and optional

They can help interpretation without replacing semantic structure.

### 7. SSC is a special validation source

It informs the adapter but does not replace the canonical contract.

## Proposal items still not fixed

Richer scene semantics and more complex routing situations remain open questions.

## Current position

The proposal phase is complete enough to serve as historical context, while the active truth now lives in the reference docs.
