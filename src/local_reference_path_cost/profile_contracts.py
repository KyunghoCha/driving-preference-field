from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ProfileSpec:
    axis: str
    coordinate: float

    @property
    def coordinate_axis(self) -> str:
        return "y" if self.axis == "horizontal" else "x"

    @property
    def sample_axis(self) -> str:
        return "x" if self.axis == "horizontal" else "y"

    def to_dict(self) -> dict[str, object]:
        return {
            "axis": self.axis,
            "coordinate": self.coordinate,
            "coordinate_axis": self.coordinate_axis,
            "sample_axis": self.sample_axis,
        }


@dataclass(frozen=True)
class ProfileSlice:
    spec: ProfileSpec
    positions: np.ndarray
    channels: dict[str, np.ndarray]

    def to_dict(self) -> dict[str, object]:
        return {
            "spec": self.spec.to_dict(),
            "positions": self.positions.tolist(),
            "channels": {name: values.tolist() for name, values in self.channels.items()},
        }


@dataclass(frozen=True)
class ComparisonProfileResult:
    spec: ProfileSpec
    baseline: ProfileSlice
    candidate: ProfileSlice
    diff: ProfileSlice

    def to_dict(self) -> dict[str, object]:
        return {
            "spec": self.spec.to_dict(),
            "baseline": self.baseline.to_dict(),
            "candidate": self.candidate.to_dict(),
            "diff": self.diff.to_dict(),
        }
