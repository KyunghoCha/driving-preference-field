from dataclasses import fields
import json
from pathlib import Path

import pytest
import yaml

from driving_preference_field.contracts import QueryContext, SemanticInputSnapshot, StateSample
from driving_preference_field.evaluator import evaluate_state
from driving_preference_field.field_runtime import build_field_runtime
from driving_preference_field.input_loader import detect_input_kind, load_semantic_input
from driving_preference_field.source_adapter import (
    GenericAdapterValidationError,
    load_generic_snapshot,
    serialize_canonical_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/adapter"


def test_generic_yaml_and_json_produce_same_canonical_summary() -> None:
    yaml_snapshot, yaml_context = load_generic_snapshot(FIXTURES / "straight_corridor_generic.yaml")
    json_snapshot, json_context = load_generic_snapshot(FIXTURES / "straight_corridor_generic.json")

    yaml_bundle = serialize_canonical_bundle(yaml_snapshot, yaml_context)
    json_bundle = serialize_canonical_bundle(json_snapshot, json_context)

    assert yaml_bundle["summary"] == json_bundle["summary"]
    assert yaml_bundle["query_context"] == json_bundle["query_context"]
    assert yaml_bundle["snapshot"]["progression_support"] == json_bundle["snapshot"]["progression_support"]


def test_generic_adapter_missing_drivable_regions_fails_validation(tmp_path) -> None:
    payload = {
        "metadata": {"name": "missing_drivable"},
        "progression_supports": [{"points": [[0.0, 0.0], [1.0, 0.0]]}],
        "query_context": {
            "query_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0},
            "local_window": {"x_min": -1.0, "x_max": 1.0, "y_min": -1.0, "y_max": 1.0},
        },
    }
    fixture = tmp_path / "missing_drivable.yaml"
    fixture.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(GenericAdapterValidationError, match="drivable_regions is required"):
        load_generic_snapshot(fixture)


def test_generic_adapter_rejects_invalid_polyline_shape(tmp_path) -> None:
    payload = {
        "drivable_regions": [{"points": [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]}],
        "progression_supports": [{"points": [[0.0, 0.0]]}],
        "query_context": {
            "query_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0},
            "local_window": {"x_min": -1.0, "x_max": 1.0, "y_min": -1.0, "y_max": 1.0},
        },
    }
    fixture = tmp_path / "bad_polyline.json"
    fixture.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(GenericAdapterValidationError, match="must contain at least 2 points"):
        load_generic_snapshot(fixture)


def test_optional_branch_and_support_metadata_are_not_required() -> None:
    snapshot, context = load_generic_snapshot(FIXTURES / "straight_corridor_generic.yaml")

    assert snapshot.metadata["name"] == "straight_corridor_generic"
    assert len(snapshot.drivable_support.regions) == 1
    assert len(snapshot.progression_support.guides) == 1
    assert context.ego_pose.x == 0.5


def test_optional_quality_and_multiple_progression_guides_are_preserved() -> None:
    bend_snapshot, _ = load_generic_snapshot(FIXTURES / "left_bend_generic.yaml")
    split_snapshot, _ = load_generic_snapshot(FIXTURES / "split_branch_generic.yaml")

    assert bend_snapshot.progression_support.guides[0].metadata["support_confidence"] == pytest.approx(0.92)
    assert len(split_snapshot.progression_support.guides) == 2
    assert len(split_snapshot.exception_layer_support.safety_regions) == 0
    assert {guide.guide_id for guide in split_snapshot.progression_support.guides} == {
        "upper_branch_progression",
        "lower_branch_progression",
    }


def test_explicit_progression_supports_take_precedence_over_global_plan_and_drivable(tmp_path) -> None:
    payload = {
        "drivable_regions": [{"points": [[0.0, -1.0], [6.0, -1.0], [6.0, 1.0], [0.0, 1.0]]}],
        "progression_supports": [{"id": "explicit", "points": [[0.0, 0.1], [6.0, 0.1]]}],
        "global_plan_supports": [{"id": "global", "points": [[0.0, 0.5], [6.0, 0.5]]}],
        "query_context": {
            "query_pose": {"x": 0.5, "y": 0.0, "yaw": 0.0},
            "local_window": {"x_min": -1.0, "x_max": 7.0, "y_min": -2.0, "y_max": 2.0},
        },
    }
    fixture = tmp_path / "explicit_wins.yaml"
    fixture.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    snapshot, _ = load_generic_snapshot(fixture)

    assert len(snapshot.progression_support.guides) == 1
    assert snapshot.progression_support.guides[0].guide_id == "explicit"
    assert snapshot.progression_support.guides[0].points[0][1] == pytest.approx(0.1)


def test_global_plan_supports_alone_become_canonical_progression_support() -> None:
    snapshot, _ = load_generic_snapshot(FIXTURES / "straight_corridor_global_plan_generic.yaml")

    assert len(snapshot.progression_support.guides) == 1
    assert snapshot.progression_support.guides[0].guide_id == "center_global_plan"
    assert snapshot.progression_support.guides[0].points[-1] == pytest.approx((6.0, 0.0))


def test_drivable_only_straight_corridor_reconstructs_single_centerline() -> None:
    snapshot, _ = load_generic_snapshot(FIXTURES / "straight_corridor_drivable_only_generic.yaml")
    guide = snapshot.progression_support.guides[0]

    assert guide.metadata["source"] == "drivable_only_reconstruction"
    assert len(guide.points) >= 2
    assert guide.points[0][0] < guide.points[-1][0]
    assert max(abs(point[1]) for point in guide.points) < 0.15


def test_drivable_only_u_turn_reconstructs_future_anchored_centerline() -> None:
    snapshot, _ = load_generic_snapshot(FIXTURES / "u_turn_drivable_only_generic.yaml")
    guide = snapshot.progression_support.guides[0]

    assert guide.metadata["source"] == "drivable_only_reconstruction"
    assert len(guide.points) >= 4
    assert guide.points[-1][1] > guide.points[0][1]
    assert guide.points[-1][0] < 2.0


def test_drivable_only_left_bend_reconstructs_curved_centerline() -> None:
    snapshot, _ = load_generic_snapshot(FIXTURES / "left_bend_drivable_only_generic.yaml")
    guide = snapshot.progression_support.guides[0]

    assert guide.metadata["source"] == "drivable_only_reconstruction"
    assert len(guide.points) >= 6
    assert guide.points[-1][0] > guide.points[0][0]
    assert guide.points[-1][1] > guide.points[0][1]
    assert guide.points[-1][1] > 4.5


def test_drivable_only_circular_arc_reconstructs_monotone_turning_centerline() -> None:
    snapshot, _ = load_generic_snapshot(FIXTURES / "circular_arc_drivable_only_generic.yaml")
    guide = snapshot.progression_support.guides[0]

    assert guide.metadata["source"] == "drivable_only_reconstruction"
    assert len(guide.points) >= 10
    assert guide.points[0][0] > 2.5
    assert guide.points[0][1] < -1.0
    assert guide.points[-1][0] < 1.0
    assert guide.points[-1][1] > 3.0


def test_drivable_only_split_branch_fails_with_explicit_ambiguity_error() -> None:
    with pytest.raises(GenericAdapterValidationError, match="ambiguous or disconnected"):
        load_generic_snapshot(FIXTURES / "split_branch_drivable_only_generic.yaml")


def test_generic_adapter_rejects_removed_branch_supports_key(tmp_path) -> None:
    payload = {
        "drivable_regions": [{"points": [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]}],
        "progression_supports": [{"points": [[0.0, 0.0], [1.0, 0.0]]}],
        "branch_supports": [{"points": [[0.5, 0.0], [1.0, 0.4]]}],
        "query_context": {
            "query_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0},
            "local_window": {"x_min": -1.0, "x_max": 1.0, "y_min": -1.0, "y_max": 1.0},
        },
    }
    fixture = tmp_path / "legacy_branch_supports.yaml"
    fixture.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(GenericAdapterValidationError, match="multiple progression_supports"):
        load_generic_snapshot(fixture)


def test_adapter_output_can_be_used_by_runtime_and_evaluator() -> None:
    snapshot, context = load_generic_snapshot(FIXTURES / "straight_corridor_generic.yaml")
    runtime = build_field_runtime(snapshot, context)
    state = StateSample(x=2.0, y=0.0, yaw=0.0)

    runtime_payload = runtime.query_state(state)
    eval_payload = evaluate_state(snapshot, context, state)

    assert runtime_payload.base_channels == eval_payload.base_preference_channels
    assert runtime_payload.base_channels["progression_tilted"] > 0.0


def test_input_loader_dispatches_toy_and_generic_paths() -> None:
    generic_loaded = load_semantic_input(FIXTURES / "straight_corridor_generic.yaml")
    drivable_loaded = load_semantic_input(FIXTURES / "straight_corridor_drivable_only_generic.yaml")
    toy_loaded = load_semantic_input(ROOT / "cases/toy/straight_corridor.yaml")

    assert detect_input_kind(FIXTURES / "straight_corridor_generic.yaml") == "generic_adapter"
    assert detect_input_kind(FIXTURES / "straight_corridor_global_plan_generic.yaml") == "generic_adapter"
    assert detect_input_kind(ROOT / "cases/toy/straight_corridor.yaml") == "toy_case"
    assert generic_loaded.input_kind == "generic_adapter"
    assert drivable_loaded.input_kind == "generic_adapter"
    assert toy_loaded.input_kind == "toy_case"


def test_query_context_owns_ego_pose_and_window_not_snapshot() -> None:
    snapshot, context = load_generic_snapshot(FIXTURES / "straight_corridor_generic.yaml")

    snapshot_fields = {field.name for field in fields(SemanticInputSnapshot)}
    context_fields = {field.name for field in fields(QueryContext)}

    assert "ego_pose" not in snapshot_fields
    assert "local_window" not in snapshot_fields
    assert "ego_pose" in context_fields
    assert "local_window" in context_fields
    assert context.semantic_snapshot is snapshot


def test_canonical_types_do_not_expose_source_specific_slots() -> None:
    snapshot_fields = {field.name for field in fields(SemanticInputSnapshot)}

    assert "lane_graph" not in snapshot_fields
    assert "ssc_route" not in snapshot_fields
    assert "planner_state" not in snapshot_fields
    assert "branch_continuity_support" not in snapshot_fields


def test_serialized_canonical_bundle_no_longer_exposes_branch_support_slot() -> None:
    snapshot, context = load_generic_snapshot(FIXTURES / "split_branch_generic.yaml")
    payload = serialize_canonical_bundle(snapshot, context)

    assert "branch_continuity_support" not in payload["snapshot"]
