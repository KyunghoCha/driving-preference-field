from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_status_docs_lock_phase5_complete_state() -> None:
    roadmap = _read("docs/status/roadmap_ko.md")
    project_status = _read("docs/status/project_status_ko.md")
    experiment_plan = _read("docs/status/experiment_plan_ko.md")

    assert "Phase 5 완료, Phase 6 준비 상태" in roadmap
    assert "Phase 5: 완료" in roadmap
    assert "reference adapter input이 SSC naming 없이 generic YAML/JSON fixture로 존재한다" in roadmap
    assert "current decision SSOT: `docs/design/source_adapter_ko.md`" in roadmap
    assert "proposal history: `docs/reading/phase5_adapter_proposal_ko.md`" in roadmap

    assert "Phase 5 완료, Phase 6 준비 상태" in project_status
    assert "generic source adapter SSOT 문서 추가" in project_status
    assert "adapter inspection / conversion CLI 추가" in project_status
    assert "docs/design/source_adapter_ko.md" in project_status
    assert "docs/reading/phase5_adapter_proposal_ko.md" in project_status

    assert "generic adapter fixture" in experiment_plan
    assert "fixtures/adapter/straight_corridor_generic.yaml" in experiment_plan


def test_source_adapter_doc_locks_phase5_canonical_contract() -> None:
    source_adapter = _read("docs/design/source_adapter_ko.md")
    input_semantics = _read("docs/design/input_semantics_ko.md")
    runtime_contract = _read("docs/design/runtime_evaluation_contract_ko.md")

    assert "adapter는 의미 번역기만 한다" in source_adapter
    assert "`SemanticInputSnapshot + QueryContext`" in source_adapter
    assert "drivable_support" in source_adapter
    assert "progression_support" in source_adapter
    assert "`ego_pose`는 snapshot 본체 의미가 아니라 QueryContext 책임이다" in source_adapter
    assert "`local_window` 크기와 slicing policy는 canonical truth가 아니라 **experiment 영역**" in source_adapter
    assert "branch winner는 canonical snapshot이 직접 정하지 않는다" in source_adapter
    assert "support/confidence/branch prior 같은 값은 있어도 **weak prior metadata**" in source_adapter
    assert "SSC는 중요한 validation source지만 canonical 기준이 아니다" in source_adapter

    assert "docs/design/source_adapter_ko.md" in input_semantics
    assert "QueryContext 또는 experiment 영역" in input_semantics

    assert "raw source -> source adapter" in runtime_contract
    assert "source adapter -> `SemanticInputSnapshot + QueryContext`" in runtime_contract
    assert "toy loader output과 generic source adapter output을 같은 canonical contract로 다룬다" in runtime_contract


def test_newcomer_docs_and_phase5_history_split_are_consistent() -> None:
    readme = _read("README.md")
    docs_index = _read("docs/index.md")
    overview = _read("docs/design/project_overview_ko.md")
    phase5_history = _read("docs/reading/phase5_adapter_proposal_ko.md")
    semantic_conditions = _read("docs/reading/semantic_support_conditions_ko.md")
    internal_status = _read("docs/internal/status.md")
    internal_priorities = _read("docs/internal/priorities.md")

    assert "Phase 5 완료, Phase 6 준비 상태" in readme
    assert "docs/design/source_adapter_ko.md" in readme
    assert "Phase 5 proposal history" in readme

    assert "Phase 5 완료, Phase 6 준비 상태" in docs_index
    assert "./design/source_adapter_ko.md" in docs_index
    assert "Phase 5 Adapter Proposal History" in docs_index
    assert "Semantic Support 조건 메모" in docs_index

    assert "`Phase 5 완료`" in overview
    assert "`Phase 6 준비 상태`" in overview
    assert "whole-space preference field" in overview
    assert "SSC는 canonical truth가 아니다" in overview

    assert "canonical 결정은 아래 design SSOT에 반영됐다" in phase5_history
    assert "docs/design/source_adapter_ko.md" in phase5_history
    assert "proposal history / reading 기록" in phase5_history

    assert "semantic support 관련 사실과 미확정 항목" in semantic_conditions
    assert "canonical truth를 새로 정의하지 않는다" in semantic_conditions
    assert "transverse 또는 longitudinal support scope를 global로 고정하는 것은 current canonical truth가 아니다" in semantic_conditions

    assert "Phase 5 is complete and the repo is in Phase 6 prep state" in internal_status
    assert "generic external-like source is translated into the canonical snapshot/context contract" in internal_status
    assert "Keep Phase 5 results stable" in internal_priorities
    assert "Keep the adapter contract generic" in internal_priorities
