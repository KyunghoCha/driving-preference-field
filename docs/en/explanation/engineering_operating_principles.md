# Engineering Operating Principles

This document records the repo's default operating direction. It is not a law book, and it is not meant to freeze the repo into one permanent process. If better evidence or a cleaner approach appears, this document can change too. The point is not obedience. The point is to keep `local-reference-path-cost` moving in ways that improve code health without letting contracts, docs, and experiments drift apart.

## 1. Start from causes, not symptoms

Local symptoms are often downstream of a wider structural problem. A quick patch is acceptable only when it is clearly scoped, easy to reason about, and does not hide the real failure mode. If a change only silences the visible symptom, it should not be treated as complete work.

The same principle applies to docs. If readers are confused, the answer is usually to clarify the canonical document, remove stale wording, or tighten the contract. Adding another note on top is rarely the best first move.

## 2. Move docs and current truth together

This repo treats explanation, reference, how-to, status, and UI help as part of the working contract. If code changes current behavior, the documents that define or explain that behavior should move in the same batch. If docs change canonical meaning, the code that claims to implement that meaning should move with them or be explicitly marked as current implementation only.

The goal is not perfect simultaneity. The goal is to avoid silent drift between what the repo says and what it does.

## 3. Reduce scope before changing internals

Requests should first be reduced to the smallest coherent slice that still solves the actual problem. If the scope is unclear, implementation quality drops quickly. This repo improves faster when one layer is stabilized at a time: canonical meaning, runtime contract, current implementation, tooling, or downstream integration.

That also means not promoting future work into current truth too early. Research ideas, adapter debates, and downstream concerns belong in reading/history or backlog documents until they are actually fixed into the active contract.

## 4. Keep SSOT above platform and downstream specifics

Platform-specific behavior should not become canonical meaning. Linux, Windows, and other environments can require different launchers, packaging, or troubleshooting steps, but the repo's semantic truth must stay above those differences. When platform issues appear, prefer fixing dependency graphs, capability detection, or runtime fallbacks instead of forking meaning by operating system.

The same logic applies to downstream consumers such as SSC. A downstream system can validate or stress the design, but it should not silently replace the repo's own contracts.

## 5. Isolate experiments from a clean baseline

Experimental work should start from a clean baseline and keep one meaningful hypothesis at a time. The exact Git mechanics can change, but the operating idea stays the same: do not keep layering experiments on top of a dirty state until the change history becomes impossible to reason about.

This principle is especially important for LRPC morphology work, where field formulas, support logic, coordinate definitions, and visualization behavior can interact in non-obvious ways. The repo should bias toward isolation and traceability over convenience.

## 6. Prefer small coherent changes and verify them end to end

Small changes are easier to reason about, easier to review, and easier to roll back. The repo should prefer a narrow, testable batch over a broad rewrite unless the broad rewrite is itself the smallest coherent move. Verification also has to be end to end. If a change touches docs, UI, runtime, exports, or experiment tooling, then all of those surfaces should be checked before the batch is treated as complete.

Emergency fixes, trusted mechanical refactors, and non-merge-targeted exploratory spikes can be exceptions, but those exceptions should be explicit. When the repo takes a shortcut, it should say so.

## 7. Review for stale residue, not only correctness

Code review should not stop at "does it work." Experimental repositories also accumulate stale formula paths, unused knobs, dead branches, outdated docs, and complexity that no longer serves a live behavior. Those are code-health problems even when the immediate output still looks plausible.

The default review question is therefore broader: does this change leave the repo easier to understand, easier to compare, and easier to evolve than before? If not, the direction probably needs to be reconsidered.

## 8. Keep the operating principles revisable

These principles are defaults, not permanent commandments. If a better process, a better baseline discipline, or a better review habit emerges, the repo should update this document explicitly instead of following it mechanically. A stable SSOT is important. A frozen process is not.
