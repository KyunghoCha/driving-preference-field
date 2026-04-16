import json
import os
from pathlib import Path
import subprocess
import sys

from driving_preference_field.cli import _load_trajectory_arg, main


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/adapter"


def test_inspect_case_outputs_slot_summary(capsys) -> None:
    case_path = ROOT / "cases/toy/straight_corridor.yaml"
    exit_code = main(["inspect-case", "--case", str(case_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["input_kind"] == "toy_case"
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
    assert "progression_anchor_count" in payload["diagnostics"]
    assert "progression_dominant_guides" in payload["diagnostics"]
    assert "base_preference_total" in payload["diagnostics"]


def test_inspect_adapter_input_outputs_generic_summary(capsys) -> None:
    fixture_path = FIXTURES / "straight_corridor_generic.yaml"
    exit_code = main(["inspect-adapter-input", "--input", str(fixture_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["input_kind"] == "generic_adapter"
    assert payload["summary"]["drivable_regions"] == 1
    assert payload["summary"]["progression_guides"] == 1


def test_convert_adapter_input_can_export_summary_yaml(tmp_path) -> None:
    fixture_path = FIXTURES / "straight_corridor_generic.yaml"
    out_path = tmp_path / "adapter_summary.yaml"

    exit_code = main(
        [
            "convert-adapter-input",
            "--input",
            str(fixture_path),
            "--out",
            str(out_path),
            "--format",
            "yaml",
            "--summary-only",
        ]
    )

    assert exit_code == 0
    text = out_path.read_text(encoding="utf-8")
    assert "input_kind: generic_adapter" in text
    assert "progression_guides: 1" in text


def test_convert_adapter_input_prints_canonical_bundle(capsys) -> None:
    fixture_path = FIXTURES / "straight_corridor_generic.yaml"
    exit_code = main(["convert-adapter-input", "--input", str(fixture_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["input_kind"] == "generic_adapter"
    assert payload["snapshot"]["progression_support"]["guides"][0]["guide_id"] == "center_progression"
    assert payload["query_context"]["ego_pose"]["x"] == 0.5


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
    assert "trajectory_soft_exception_total" not in payload


def test_inline_trajectory_json_is_parsed_before_path_probe(monkeypatch) -> None:
    class _ForbiddenPath:
        def __init__(self, *_args, **_kwargs) -> None:
            raise AssertionError("Path probing should not happen for inline trajectory JSON")

    monkeypatch.setattr("driving_preference_field.cli.Path", _ForbiddenPath)

    trajectory = _load_trajectory_arg('{"states":[{"x":1.0,"y":2.0,"yaw":0.5}]}')

    assert len(trajectory.states) == 1
    assert trajectory.states[0].x == 1.0
    assert trajectory.states[0].y == 2.0
    assert trajectory.states[0].yaw == 0.5


def test_parameter_lab_cli_starts_and_returns_zero(monkeypatch) -> None:
    case_path = FIXTURES / "straight_corridor_generic.yaml"

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


def test_parameter_lab_import_path_does_not_import_matplotlib() -> None:
    script = """
import json
import sys
import driving_preference_field
payload = {"package": "matplotlib" in sys.modules}
import driving_preference_field.cli
payload["cli"] = "matplotlib" in sys.modules
import driving_preference_field.ui.parameter_lab_window
payload["window"] = "matplotlib" in sys.modules
print(json.dumps(payload, sort_keys=True))
"""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"cli": False, "package": False, "window": False}
