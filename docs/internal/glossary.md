# Internal Glossary

## base driving preference field

A spatial preference structure that encodes ideal driving desirability before obstacle/rule exceptions are applied.

## input semantics

Externally supplied drivable semantics and progression semantics used to generate the base field.

## progression semantics

Direction, continuity, and branch-related meaning that lets the field generator build a progression-tilted preference structure.

## local analytic evaluation

Runtime evaluation of the field in an ego-centric local region without requiring a full dense raster.

## exception layers

Safety, rule, and dynamic-interaction layers that are not treated as identical to the base field.

## semantic slots

Source-independent input slots such as drivable support, progression support, boundary/interior support, and branch/continuity support.

## hard violation flags

Boolean or categorical indicators that a candidate state or trajectory violates a safety, rule, or dynamic restriction that must not be canceled by base preference.
