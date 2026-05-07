import json
from pathlib import Path

from local_reference_path_cost.cli import main
from local_reference_path_cost.raster import sample_local_raster
from local_reference_path_cost.rendering import render_case
from local_reference_path_cost.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_raster_sampler_produces_requested_shape() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    raster = sample_local_raster(snapshot, context, x_samples=32, y_samples=24)

    assert raster.channels["progression_tilted"].shape == (24, 32)
    assert raster.channels["hard_unsafe_mask"].dtype == bool


def test_raster_sampler_keeps_missing_rule_and_dynamic_as_zero() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/sensor_patch_open.yaml")
    raster = sample_local_raster(snapshot, context, x_samples=16, y_samples=16)

    assert float(raster.channels["rule_soft"].max()) == 0.0
    assert float(raster.channels["dynamic_soft"].max()) == 0.0
    assert int(raster.channels["hard_rule_mask"].sum()) == 0
    assert int(raster.channels["hard_dynamic_mask"].sum()) == 0


def test_render_case_writes_expected_files_and_summary(tmp_path: Path) -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/merge_like_patch.yaml")
    artifacts = render_case(
        snapshot,
        context,
        case_name="merge_like_patch",
        out_dir=tmp_path / "render",
        x_samples=40,
        y_samples=40,
    )

    expected = {
        "progression_tilted.png",
        "progression_s_hat.png",
        "progression_center_distance.png",
        "progression_longitudinal_component.png",
        "progression_transverse_term.png",
        "safety_soft.png",
        "rule_soft.png",
        "dynamic_soft.png",
        "hard_unsafe_mask.png",
        "hard_rule_mask.png",
        "hard_dynamic_mask.png",
        "composite_debug.png",
        "render_legend.png",
        "render_summary.json",
    }
    assert expected.issubset(set(artifacts.file_manifest))
    summary_path = Path(artifacts.file_manifest["render_summary.json"])
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["hard_mask_pixel_counts"]["hard_unsafe_mask"] >= 0
    assert "progression_tilted" in summary["channel_ranges"]
    assert "progression_tilted" in summary["channel_descriptions"]
    assert "render_legend.png" in summary["render_file_manifest"]
    legend_text = (tmp_path / "render" / "render_legend.png").read_bytes()
    assert legend_text


def test_render_case_cli_exports_pngs_and_summary(tmp_path: Path, capsys) -> None:
    case_path = ROOT / "cases/toy/sensor_patch_open.yaml"
    out_dir = tmp_path / "sensor_render"
    exit_code = main(
        [
            "render-case",
            "--case",
            str(case_path),
            "--out-dir",
            str(out_dir),
            "--x-samples",
            "24",
            "--y-samples",
            "20",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert (out_dir / "composite_debug.png").exists()
    assert (out_dir / "render_legend.png").exists()
    assert (out_dir / "render_summary.json").exists()
    assert payload["summary"]["raster_resolution"]["x_samples"] == 24
