from pathlib import Path

import pytest

from driving_preference_field.toy_loader import load_toy_snapshot, summarize_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_toy_loader_builds_semantic_snapshot() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")

    assert snapshot.metadata["name"] == "straight_corridor"
    assert len(snapshot.drivable_support.regions) == 1
    assert len(snapshot.progression_support.guides) == 1
    assert context.ego_pose.x == 0.5
    assert context.local_window.x_max == 7.0


def test_summarize_snapshot_reports_slot_counts() -> None:
    snapshot, _ = load_toy_snapshot(ROOT / "cases/toy/split_branch.yaml")
    summary = summarize_snapshot(snapshot)

    assert summary["drivable_regions"] == 1
    assert summary["progression_guides"] == 2
    assert len(snapshot.exception_layer_support.safety_regions) == 0
    assert "branch_guides" not in summary


def test_sensor_only_open_patch_loads_expected_metadata() -> None:
    snapshot, _ = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_open.yaml")

    assert snapshot.metadata["name"] == "sensor_patch_open"
    assert len(snapshot.progression_support.guides) == 1
    assert snapshot.progression_support.guides[0].weight < 0.5


def test_u_turn_case_loads_expected_metadata() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn.yaml")

    assert snapshot.metadata["name"] == "u_turn"
    assert len(snapshot.drivable_support.regions) == 1
    assert len(snapshot.progression_support.guides) == 1
    assert len(snapshot.boundary_interior_support.boundaries) == 2
    assert context.ego_pose.yaw == 0.0


def test_u_turn_many_small_guides_case_loads_expected_metadata() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/u_turn_many_small_progression_guides.yaml")

    assert snapshot.metadata["name"] == "u_turn_many_small_progression_guides"
    assert snapshot.metadata["progression_normalization"]["source_kind"] == "toy_case"
    assert snapshot.metadata["progression_normalization"]["applied"] is True
    assert snapshot.metadata["progression_normalization"]["severity"] == "warning"
    assert len(snapshot.drivable_support.regions) == 1
    assert len(snapshot.progression_support.guides) == 1
    assert snapshot.progression_support.guides[0].metadata["normalized_from"] == [
        f"u_turn_seg_{index:02d}" for index in range(1, 11)
    ]
    assert len(snapshot.boundary_interior_support.boundaries) == 2
    assert context.ego_pose.yaw == 0.0


def test_two_lane_straight_case_loads_parallel_progression_guides() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/two_lane_straight.yaml")
    summary = summarize_snapshot(snapshot)

    assert snapshot.metadata["name"] == "two_lane_straight"
    assert len(snapshot.drivable_support.regions) == 1
    assert len(snapshot.progression_support.guides) == 2
    assert summary["progression_guides"] == 2
    assert context.ego_pose.y == -0.6


def test_toy_loader_rejects_removed_branch_guides_key(tmp_path) -> None:
    fixture = tmp_path / "legacy_branch_guides.yaml"
    fixture.write_text(
        """
metadata:
  name: legacy
query_window: {x_min: -1.0, x_max: 1.0, y_min: -1.0, y_max: 1.0}
ego_pose: {x: 0.0, y: 0.0, yaw: 0.0}
drivable_regions:
  - points: [[0.0, -1.0], [1.0, -1.0], [1.0, 1.0], [0.0, 1.0]]
progression_guides:
  - points: [[0.0, 0.0], [1.0, 0.0]]
branch_guides:
  - points: [[0.5, 0.0], [1.0, 0.5]]
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="multiple progression_guides"):
        load_toy_snapshot(fixture)
