from pathlib import Path

from driving_preference_field.contracts import StateSample, TrajectorySample
from driving_preference_field.evaluator import evaluate_state, evaluate_trajectory
from driving_preference_field.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_ordering_key_prefers_higher_progression_total() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    preferred = TrajectorySample(
        states=(
            StateSample(x=1.0, y=0.0, yaw=0.0),
            StateSample(x=2.0, y=0.0, yaw=0.0),
        )
    )
    off_axis = TrajectorySample(
        states=(
            StateSample(x=1.0, y=0.8, yaw=0.0),
            StateSample(x=2.0, y=0.8, yaw=0.0),
        )
    )

    good_result = evaluate_trajectory(snapshot, context, preferred)
    bad_result = evaluate_trajectory(snapshot, context, off_axis)

    assert good_result.ordering_key < bad_result.ordering_key


def test_state_evaluation_exposes_progression_only_base_channel() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    state = StateSample(x=4.7, y=2.0, yaw=1.0)
    result = evaluate_state(snapshot, context, state)

    assert set(result.base_preference_channels) == {"progression_tilted"}


def test_blocked_sensor_patch_keeps_progression_score_queryable() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_blocked.yaml")
    blocked = StateSample(x=3.2, y=0.0, yaw=0.0)
    result = evaluate_state(snapshot, context, blocked)

    assert result.base_preference_channels["progression_tilted"] > 0.0


def test_state_diagnostics_include_progression_fields_only() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    state = StateSample(x=3.4, y=0.25, yaw=-0.2)
    result = evaluate_state(snapshot, context, state)

    assert "progression_anchor_count" in result.diagnostics
    assert "progression_effective_anchor_count" in result.diagnostics
    assert "progression_support_mod" in result.diagnostics
    assert "progression_alignment_mod" in result.diagnostics
    assert "progression_dominant_guides" in result.diagnostics
    assert "base_preference_total" in result.diagnostics
