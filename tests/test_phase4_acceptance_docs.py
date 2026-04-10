from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_status_docs_lock_late_phase4_acceptance() -> None:
    roadmap = _read("docs/status/roadmap_ko.md")
    project_status = _read("docs/status/project_status_ko.md")
    experiment_plan = _read("docs/status/experiment_plan_ko.md")

    assert "late Phase 4 acceptance" in roadmap
    assert "semantic-first" in roadmap
    assert "Phase 4 완료, Phase 5 준비 상태" in roadmap
    assert "overlap 영역 ordering stability" in roadmap
    assert "visible endpoint가 semantic start/end처럼 보이지 않는다" in roadmap
    assert "`straight_corridor`, `left_bend`, `split_branch`, `merge_like_patch`, `u_turn`" in roadmap
    assert "Parameter Lab export만으로 morphology 비교가 재현 가능하다" in roadmap
    assert "위 acceptance를 현재 문서 / 구현 / 테스트 기준으로 충족한 상태로 본다" in roadmap
    assert "docs/reading/phase5_adapter_proposal_ko.md" in roadmap

    assert "late Phase 4 acceptance lock" in project_status
    assert "Phase 4 완료, Phase 5 준비 상태" in project_status
    assert "FieldRuntime" in project_status
    assert "fake end-cap" in project_status
    assert "Gazebo / RViz / MPPI hookup" in project_status
    assert "위 종료 조건은 충족한 상태로 본다" in project_status
    assert "docs/reading/phase5_adapter_proposal_ko.md" in project_status

    assert "late Phase 4 semantic acceptance" in experiment_plan
    assert "overlap 영역 ordering flip" in experiment_plan
    assert "visible endpoint saturation wall 또는 fake end-cap" in experiment_plan
    assert "ordering 보존" in experiment_plan
    assert "continuity 유지" in experiment_plan
    assert "local peak 부재" in experiment_plan


def test_runtime_contract_doc_locks_public_interface_for_phase4() -> None:
    runtime_contract = _read("docs/design/runtime_evaluation_contract_ko.md")

    assert "`build_field_runtime(snapshot, context, config=None)`" in runtime_contract
    assert "`FieldRuntime.query_state(state)`" in runtime_contract
    assert "`FieldRuntime.query_trajectory(trajectory)`" in runtime_contract
    assert "`FieldRuntime.query_debug_grid(x_coords, y_coords)`" in runtime_contract
    assert "virtual continuation" in runtime_contract
    assert "cache 사용 여부가 semantic drift를 만들지 않는다" in runtime_contract
    assert "downstream consumer는 current formula를 복제하지 않고 이 runtime layer를 소비" in runtime_contract


def test_newcomer_overview_and_phase5_reading_split_are_locked() -> None:
    readme = _read("README.md")
    docs_index = _read("docs/index.md")
    overview = _read("docs/design/project_overview_ko.md")
    phase5_proposal = _read("docs/reading/phase5_adapter_proposal_ko.md")
    base_foundation = _read("docs/design/base_field_foundation_ko.md")
    input_semantics = _read("docs/design/input_semantics_ko.md")
    parameter_lab = _read("docs/design/parameter_lab_ko.md")

    assert "docs/design/project_overview_ko.md" in readme
    assert "./design/project_overview_ko.md" in docs_index
    assert "Phase 4 완료, Phase 5 준비 상태" in readme
    assert "Phase 4 완료, Phase 5 준비 상태" in docs_index
    assert "Phase 5 Adapter Proposal" in docs_index
    assert "docs/reading/phase5_adapter_proposal_ko.md" in readme

    assert "whole-space preference field" in overview
    assert "progression과 drivable을 왜 분리해서 보는가" in overview
    assert "공간을 알려주지 방향을 직접 고르지 않는다" in overview
    assert "SSC는 canonical truth가 아니다" in overview
    assert "`Phase 4 완료`" in overview
    assert "`Phase 5 준비 상태`" in overview

    assert "canonical design SSOT가 아니다" in phase5_proposal
    assert "의미 번역기만" in phase5_proposal
    assert "Phase 5 준비용 reading 문서" in phase5_proposal

    assert "source adapter가 이것을 어떤 raw structure에서 어떻게 번역할지는 아직 Phase 5 proposal / experiment 영역" in input_semantics
    assert "downstream integration tool이 아니라 **whole-space field morphology를 읽고 비교하는 해석 도구**" in parameter_lab
    assert "공간을 알려주지 방향을 직접 고르지 않는다" in base_foundation
