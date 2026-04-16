from pathlib import Path

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
    assert summary["progression_guides"] == 1
    assert summary["branch_guides"] == 2


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


def test_two_lane_straight_case_loads_parallel_progression_guides() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/two_lane_straight.yaml")
    summary = summarize_snapshot(snapshot)

    assert snapshot.metadata["name"] == "two_lane_straight"
    assert len(snapshot.drivable_support.regions) == 1
    assert len(snapshot.progression_support.guides) == 2
    assert summary["progression_guides"] == 2
    assert summary["branch_guides"] == 0
    assert context.ego_pose.y == -0.9
