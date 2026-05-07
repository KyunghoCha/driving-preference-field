from pathlib import Path
import json

import numpy as np

from local_reference_path_cost.profile_inspection import (
    ProfileSpec,
    build_comparison_profile,
    export_profile_bundle,
)
from local_reference_path_cost.raster import sample_local_raster
from local_reference_path_cost.toy_loader import load_toy_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_build_comparison_profile_exposes_selected_and_debug_channels() -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/straight_corridor.yaml")
    baseline = sample_local_raster(snapshot, context, x_samples=40, y_samples=32)
    candidate = sample_local_raster(snapshot, context, x_samples=40, y_samples=32)

    result = build_comparison_profile(
        baseline,
        candidate,
        spec=ProfileSpec(axis="horizontal", coordinate=0.0),
        selected_channel="progression_tilted",
    )

    assert result.baseline.positions.shape == (40,)
    assert "progression_tilted" in result.baseline.channels
    assert "progression_s_hat" in result.baseline.channels
    assert "progression_center_distance" in result.baseline.channels
    assert np.allclose(result.diff.channels["progression_tilted"], 0.0)


def test_export_profile_bundle_writes_pngs_and_json(tmp_path: Path) -> None:
    snapshot, context = load_toy_snapshot(ROOT / "cases/toy/left_bend.yaml")
    baseline = sample_local_raster(snapshot, context, x_samples=48, y_samples=40)
    candidate = sample_local_raster(snapshot, context, x_samples=48, y_samples=40)

    result = build_comparison_profile(
        baseline,
        candidate,
        spec=ProfileSpec(axis="vertical", coordinate=4.5),
        selected_channel="progression_tilted",
    )
    payload = export_profile_bundle(
        result,
        selected_channel="progression_tilted",
        out_dir=tmp_path / "profile",
    )

    assert (tmp_path / "profile" / "profile_baseline.png").exists()
    assert (tmp_path / "profile" / "profile_candidate.png").exists()
    assert (tmp_path / "profile" / "profile_diff.png").exists()
    assert (tmp_path / "profile" / "profile_data.json").exists()
    exported = json.loads((tmp_path / "profile" / "profile_data.json").read_text(encoding="utf-8"))
    assert exported["selected_channel"] == "progression_tilted"
    assert payload["summary"]["selected_channel"] == "progression_tilted"
