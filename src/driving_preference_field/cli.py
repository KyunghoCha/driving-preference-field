from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .config import DEFAULT_FIELD_CONFIG
from .contracts import StateSample, TrajectorySample
from .evaluator import evaluate_state, evaluate_trajectory
from .rendering import render_case
from .toy_loader import load_toy_snapshot, summarize_snapshot


def _load_trajectory_arg(raw: str) -> TrajectorySample:
    candidate = Path(raw)
    if candidate.exists():
        payload = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    else:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = yaml.safe_load(raw)
    states = payload["states"] if isinstance(payload, dict) else payload
    return TrajectorySample(
        states=tuple(
            StateSample(x=float(item["x"]), y=float(item["y"]), yaw=float(item["yaw"]))
            for item in states
        )
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="driving_preference_field")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect-case")
    inspect_parser.add_argument("--case", required=True)

    eval_state_parser = subparsers.add_parser("evaluate-state")
    eval_state_parser.add_argument("--case", required=True)
    eval_state_parser.add_argument("--x", required=True, type=float)
    eval_state_parser.add_argument("--y", required=True, type=float)
    eval_state_parser.add_argument("--yaw", required=True, type=float)

    eval_trajectory_parser = subparsers.add_parser("evaluate-trajectory")
    eval_trajectory_parser.add_argument("--case", required=True)
    eval_trajectory_parser.add_argument("--trajectory", required=True)

    render_case_parser = subparsers.add_parser("render-case")
    render_case_parser.add_argument("--case", required=True)
    render_case_parser.add_argument("--out-dir")
    render_case_parser.add_argument("--x-samples", type=int, default=160)
    render_case_parser.add_argument("--y-samples", type=int, default=160)
    render_case_parser.add_argument("--dpi", type=int, default=160)

    parameter_lab_parser = subparsers.add_parser("parameter-lab")
    parameter_lab_parser.add_argument("--case")
    parameter_lab_parser.add_argument("--baseline-preset")
    parameter_lab_parser.add_argument("--candidate-preset")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "parameter-lab":
        from PyQt6.QtWidgets import QApplication

        from .ui.parameter_lab_window import ParameterLabWindow

        app = QApplication.instance() or QApplication([])
        window = ParameterLabWindow(
            case_path=Path(args.case) if args.case else None,
            baseline_preset=Path(args.baseline_preset) if args.baseline_preset else None,
            candidate_preset=Path(args.candidate_preset) if args.candidate_preset else None,
        )
        window.show()
        return app.exec()

    snapshot, context = load_toy_snapshot(args.case)

    if args.command == "inspect-case":
        payload = {
            "case": str(args.case),
            "summary": summarize_snapshot(snapshot),
            "query_window": {
                "x_min": context.local_window.x_min,
                "x_max": context.local_window.x_max,
                "y_min": context.local_window.y_min,
                "y_max": context.local_window.y_max,
            },
            "ego_pose": {
                "x": context.ego_pose.x,
                "y": context.ego_pose.y,
                "yaw": context.ego_pose.yaw,
            },
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "evaluate-state":
        state = StateSample(x=args.x, y=args.y, yaw=args.yaw)
        result = evaluate_state(snapshot, context, state)
        payload = {
            "state": {"x": state.x, "y": state.y, "yaw": state.yaw},
            "base_preference_channels": result.base_preference_channels,
            "base_preference_total": result.base_preference_total,
            "soft_exception_channels": result.soft_exception_channels,
            "soft_exception_total": result.soft_exception_total,
            "hard_violation_flags": result.hard_violation_flags,
            "diagnostics": result.diagnostics,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "evaluate-trajectory":
        trajectory = _load_trajectory_arg(args.trajectory)
        result = evaluate_trajectory(snapshot, context, trajectory)
        payload = {
            "trajectory_size": len(trajectory.states),
            "trajectory_base_preference_channels": result.trajectory_base_preference_channels,
            "trajectory_base_preference_total": result.trajectory_base_preference_total,
            "trajectory_soft_exception_channels": result.trajectory_soft_exception_channels,
            "trajectory_soft_exception_total": result.trajectory_soft_exception_total,
            "trajectory_hard_violation_flags": result.trajectory_hard_violation_flags,
            "trajectory_hard_violation_count": sum(
                1 for value in result.trajectory_hard_violation_flags.values() if value
            ),
            "ordering_key": list(result.ordering_key),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "render-case":
        case_name = str(snapshot.metadata.get("name", Path(args.case).stem))
        artifacts = render_case(
            snapshot,
            context,
            case_name=case_name,
            config=DEFAULT_FIELD_CONFIG,
            out_dir=args.out_dir,
            x_samples=args.x_samples,
            y_samples=args.y_samples,
            dpi=args.dpi,
        )
        payload = {
            "case_name": case_name,
            "out_dir": str(artifacts.out_dir),
            "render_file_manifest": artifacts.file_manifest,
            "summary": artifacts.summary,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
