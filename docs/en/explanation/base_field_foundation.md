# Reference-Path Cost Model Foundation

This document explains what the reference-path cost model is supposed to mean before any particular implementation detail is considered. It answers one question: what kind of object is the core local reference path cost supposed to be?

## Why a single reference is not enough

A single reference path can tell a system where one intended centerline lies, but it cannot fully explain local ordering structure. It does not directly say which nearby states are still compatible with good motion, how the field should behave when multiple continuations exist, or how an optimizer should rank one region against another without committing to a winner too early.

That is why this repo does not start from “pick the correct path.” It starts from “define a useful ordering over the local map.”

## What the reference-path cost model is

The reference-path cost model is a local reference path cost surface over the visible local map. Higher values are better. The field should let a downstream consumer compare states or trajectories even when they are not exactly on one centerline. It is not a discrete route choice. It is an ordering surface.

## Why progression and drivable are separated

Progression semantics describe intended forward flow: what counts as before and after, what continuation is compatible with the local scene, and how local ordering should change across the map. Drivable semantics describe where motion is currently possible or supported.

These are different questions. If they are collapsed too early, the field becomes harder to interpret. This repo therefore treats progression as the main source of base ordering and treats drivable support as domain, support, and reconstruction input.

## Properties the field should have

The field should cover the local map, not only the guide line itself. It should expose meaningful longitudinal and transverse structure. It should make ordering available to an optimizer without hard-coding the final winner direction. It should also remain source-agnostic enough that different upstream providers can feed it through a stable adapter contract.

## Why support and gate are secondary

Support, confidence, and gate-like effects still matter, but they are secondary. They can shape how trustworthy or strong a local ordering should be, yet they should not replace the base semantic meaning. If support dominates too early, the field starts looking like a geometry or occupancy score rather than a progression-centered reference-path cost surface.

## How the current implementation approximates the concept

The current implementation approximates the reference-path cost model through `progression_tilted` and related guide-local detail channels. It uses progression guides to build local coordinates and a score surface, then exposes that result as the base ordering. Drivable boundaries are treated as overlay and support. Obstacle, rule, and dynamic actor signals are kept in separate cost-like layers rather than folded into the base score.

## The layer this field is responsible for

The reference-path cost model is upstream of the final optimizer choice but downstream of raw scene reconstruction. It is the layer that says “this region is better than that region” before the consumer decides exactly how to move. That is the level this repo is responsible for.
