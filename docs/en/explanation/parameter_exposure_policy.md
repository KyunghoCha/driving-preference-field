# Parameter Exposure Policy

This document explains how knobs should be exposed in `local-reference-path-cost`. The core question is not whether a value can be changed, but whether exposing it helps users reason about the field without turning the tool into a pile of implementation details.

Not every tunable belongs in the main GUI. Some parameters change the visible semantics and should be easy to reach. Others only tune morphology quality or runtime behavior and should stay behind an advanced surface. Some values are internal safety guards and should not be promoted into the user-facing interface at all.

This repo therefore uses three tiers.

`Main` parameters are the controls a user should touch first when reading field meaning. These are the knobs that directly change longitudinal framing, longitudinal family, transverse family, or main scale-like behavior. They belong in the visible parameter panel because they are part of how the user interprets the field.

`Advanced` parameters are still legitimate tuning knobs, but they are research controls rather than day-one controls. Discretization density, support kernel shape, and modulation ranges belong here. These values can matter a lot, but they usually matter after a user already understands the main semantic controls.

`Internal` values are not a GUI surface. Numerical epsilons, cache guards, and low-level implementation constants exist to keep the runtime safe or predictable. Exposing them would increase confusion more than it would improve understanding.

This tiering also affects layout. The left-side `Workspace` is for reading outputs such as presets, summary, profiles, and overlays. The right-side `Parameters` dock is the place for controls. If an advanced knob is promoted, it should still stay on the right side and remain secondary to the main semantic controls.

The rule for adding a new exposed knob is straightforward. First add it to the reference catalog. Then decide whether it belongs to `Main`, `Advanced`, or `Internal`. Promotion to `Main` should only happen when the value is useful for interpreting score semantics directly rather than only tuning implementation quality.
