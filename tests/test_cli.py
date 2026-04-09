import json
from pathlib import Path

from driving_preference_field.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_inspect_case_outputs_slot_summary(capsys) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    exit_code = main(["inspect-case", "--case", str(case_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["summary"]["progression_guides"] == 1


def test_evaluate_state_outputs_layerwise_result(capsys) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    exit_code = main(
        [
            "evaluate-state",
            "--case",
            str(case_path),
            "--x",
            "2.0",
            "--y",
            "0.0",
            "--yaw",
            "0.0",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "base_preference_channels" in payload
    assert "hard_violation_flags" in payload
    assert "progression_anchor_count" in payload["diagnostics"]
    assert "progression_dominant_guides" in payload["diagnostics"]
    assert "interior_signed_margin" in payload["diagnostics"]


def test_evaluate_trajectory_outputs_ordering_key(capsys) -> None:
    case_path = ROOT / "cases/toy/split_branch.yaml"
    trajectory = '{"states":[{"x":4.6,"y":1.0,"yaw":0.55},{"x":5.3,"y":1.5,"yaw":0.55}]}'
    exit_code = main(
        [
            "evaluate-trajectory",
            "--case",
            str(case_path),
            "--trajectory",
            trajectory,
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "ordering_key" in payload
    assert "trajectory_base_preference_total" in payload


def test_parameter_lab_cli_starts_and_returns_zero(monkeypatch) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"

    class _FakeApp:
        @staticmethod
        def instance():
            return None

        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        def exec(self) -> int:
            return 0

    class _FakeWindow:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        def show(self) -> None:
            return None

    monkeypatch.setattr("PyQt6.QtWidgets.QApplication", _FakeApp)
    monkeypatch.setattr("driving_preference_field.ui.parameter_lab_window.ParameterLabWindow", _FakeWindow)

    exit_code = main(["parameter-lab", "--case", str(case_path)])

    assert exit_code == 0
