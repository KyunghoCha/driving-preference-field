from pathlib import Path

from driving_preference_field.contracts import StateSample, TrajectorySample
from driving_preference_field.evaluator import evaluate_state, evaluate_trajectory
from driving_preference_field.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_hard_violation_persists_across_trajectory() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    trajectory = TrajectorySample(
        states=(
            StateSample(x=2.0, y=0.0, yaw=0.0),
            StateSample(x=4.2, y=1.95, yaw=0.0),
        )
    )

    result = evaluate_trajectory(snapshot, context, trajectory)

    assert result.trajectory_hard_violation_flags["unsafe"] is True


def test_ordering_key_prioritizes_hard_then_soft_then_base() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    preferred = TrajectorySample(
        states=(
            StateSample(x=1.0, y=0.0, yaw=0.0),
            StateSample(x=2.0, y=0.0, yaw=0.0),
        )
    )
    violated = TrajectorySample(
        states=(
            StateSample(x=4.2, y=1.95, yaw=0.0),
            StateSample(x=4.25, y=2.0, yaw=0.0),
        )
    )

    good_result = evaluate_trajectory(snapshot, context, preferred)
    bad_result = evaluate_trajectory(snapshot, context, violated)

    assert good_result.ordering_key < bad_result.ordering_key


def test_state_evaluation_keeps_base_and_exception_channels_separate() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    state = StateSample(x=4.7, y=2.0, yaw=1.0)
    result = evaluate_state(snapshot, context, state)

    assert set(result.base_preference_channels) == {
        "progression_tilted",
        "interior_boundary",
        "continuity_branch",
    }
    assert set(result.soft_exception_channels) == {
        "safety_soft",
        "rule_soft",
        "dynamic_soft",
    }


def test_blocked_sensor_patch_keeps_hard_soft_separate() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_blocked.yaml")
    blocked = StateSample(x=3.2, y=0.0, yaw=0.0)
    result = evaluate_state(snapshot, context, blocked)

    assert result.base_preference_channels["progression_tilted"] > 0.0
    assert result.hard_violation_flags["unsafe"] is True
    assert result.soft_exception_channels["safety_soft"] > 0.0


def test_state_diagnostics_include_phase2_fields() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    state = StateSample(x=3.4, y=0.25, yaw=-0.2)
    result = evaluate_state(snapshot, context, state)

    assert "progression_anchor_count" in result.diagnostics
    assert "progression_support_mod" in result.diagnostics
    assert "progression_alignment_mod" in result.diagnostics
    assert "progression_dominant_guides" in result.diagnostics
    assert "interior_signed_margin" in result.diagnostics
    assert "nearest_branch_guide_id" in result.diagnostics
    assert "base_preference_total" in result.diagnostics
    assert "soft_exception_total" in result.diagnostics
