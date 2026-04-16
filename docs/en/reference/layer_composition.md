# Layer Composition

This page defines how the repo separates the base field from other layers. It is a reference page about composition rules, not a current implementation walkthrough.

## Basic rule

The progression-centered base field should remain conceptually separate from drivable support, geometry priors, and exception-style layers. If everything is merged too early, the field becomes harder to interpret and harder to compare across sources.

## Composition rules

- the base field carries the main progression-centered ordering
- drivable support acts as domain, support, or reconstruction input
- geometry priors may influence interpretation but should remain secondary
- obstacle, rule, and dynamic layers remain separate burden or cost-like layers

## Prototype default order

The base field comes first. Support and geometry modulation come second. Exception-style layers remain outside the base score and should be consumed as separate overlays or penalties by downstream tooling.

## Out of scope

This page does not define one final planner objective, one optimizer loss, or one downstream control policy. Those are consumer concerns.

## Current baseline

The current runtime keeps `progression_tilted` as the base score and separates obstacle / rule / dynamic channels into costmap-style views.
