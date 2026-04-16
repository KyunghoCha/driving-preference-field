# Engineering Operating Principles

This document explains how the repo should be changed without drifting away from its own contracts. It is not a checklist of habits. It is a set of engineering rules for deciding what to change, what not to change, and what must move together.

## 1. Fix causes before symptoms

Local symptoms are often downstream of a wider structural problem. A quick patch is acceptable only when it is clearly scoped, easy to reason about, and does not hide the real failure mode. If a change only silences the visible symptom, it should not be treated as complete work.

That rule applies to docs as much as code. If readers are confused, the answer is not to add another note on top. The answer is usually to clarify the canonical document, remove stale wording, or make the contract more explicit.

## 2. Move docs and current truth together

This repo keeps explanation, reference, how-to, status, and UI help as part of the working contract. If code changes the current behavior, the documents that define or explain that behavior must move in the same batch. If docs change the canonical meaning, the code that claims to implement it must be checked in the same batch or explicitly marked as current implementation only.

The goal is not perfect simultaneity. The goal is to avoid silent drift between what the repo says and what it does.

## 3. Cut scope before changing internals

A request should first be reduced to the smallest coherent slice that still solves the actual problem. If the scope is unclear, implementation quality drops quickly. This repo tends to improve faster when one layer is stabilized at a time: canonical meaning, runtime contract, current implementation, tooling, or downstream integration.

That also means not promoting future work into current truth too early. Research ideas, adapter debates, and downstream concerns belong in reading/history or backlog documents until they are actually fixed into the active contract.

## 4. Keep SSOT above platform-specific behavior

Platform-specific behavior should not become canonical meaning. Linux, Windows, and other environments can require different launchers, packaging, or troubleshooting steps, but the repo’s semantic truth must stay above those differences. When platform issues appear, prefer fixing dependency graphs, capability detection, or runtime fallbacks instead of forking meaning by operating system.

The same logic applies to downstream sources such as SSC. A downstream consumer can validate the design, but it should not silently replace the repo’s own contracts.

## 5. Keep changes small and verify them end to end

Small changes are easier to reason about, easier to review, and easier to rollback. The repo should prefer a narrow, testable batch over a broad rewrite unless the broad rewrite is itself the smallest coherent move. Verification also has to be end to end. If a change touches docs, UI, runtime, and exports, then all of those surfaces must be checked before the batch is considered complete.

In practice, this means every meaningful change should leave behind two things: a clearer current truth and a stronger regression boundary.
