# Reference-Path Cost Model Terms

This page lists the main terms used when discussing the reference-path cost model. It is a lookup document, not a design essay.

## Required terms

### 1. Progression-aware potential structure

The progression-centered part of the field that defines the main ordering over the local map.

### 2. Interior / boundary-derived preference

Geometry-derived preference that can act as support or prior, but is not the canonical reference-path cost model itself.

### 3. Continuity / branch structure

The way multiple valid continuations are represented without forcing an early branch winner. In the current implementation this is expressed through multiple progression guides rather than a separate branch-guide layer.

## Optional / experimental terms

Support modulation, alignment modulation, exception layers, and morphology tuning terms can be used when needed, but they should not be confused with the canonical base meaning.

## Relationship between terms

Progression is the main source of base ordering. Drivable and geometry-derived terms constrain or support interpretation. Exception layers remain separate from the reference-path cost model. Downstream optimizers consume the field; they do not replace its meaning.

## Current baseline

For exact current-runtime formulas, see [Current Formula Reference](./current_formula_reference.md). For conceptual framing, see [Reference-Path Cost Model Foundation](../explanation/base_field_foundation.md).
