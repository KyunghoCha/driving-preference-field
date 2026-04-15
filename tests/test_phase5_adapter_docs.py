from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_is_short_landing_page() -> None:
    readme = _read("README.md")

    assert "Phase 5 완료, Phase 6 준비 상태" in readme
    assert "docs/index.md" in readme
    assert "docs/explanation/project_overview_ko.md" in readme
    assert "docs/reference/source_adapter_ko.md" in readme
    assert "docs/reference/current_formula_reference_ko.md" in readme
    assert "## 현재 수식 요약" not in readme
    assert "## Parameter Lab" not in readme
    assert "docs/design/" not in readme


def test_docs_index_exposes_newcomer_spine_and_role_tables() -> None:
    docs_index = _read("docs/index.md")

    assert "Phase 5 완료, Phase 6 준비 상태" in docs_index
    assert "## Newcomer Spine" in docs_index
    assert "./explanation/project_overview_ko.md" in docs_index
    assert "./reference/source_adapter_ko.md" in docs_index
    assert "./how-to/parameter_lab_ko.md" in docs_index
    assert "./reading/source/input_reconstruction_notes_ko.md" in docs_index
    assert "./reading/history/phase5_adapter_proposal_ko.md" in docs_index
    assert "./reading/references/external_references_ko.md" in docs_index
    assert "| 문서 | canonical | 대상 독자 | 언제 읽는지 |" in docs_index
    assert "./design/" not in docs_index


def test_canonical_docs_use_new_paths_metadata_and_numbered_titles() -> None:
    overview = _read("docs/explanation/project_overview_ko.md")
    principles = _read("docs/explanation/engineering_operating_principles_ko.md")
    scope = _read("docs/explanation/research_scope_ko.md")
    foundation = _read("docs/explanation/base_field_foundation_ko.md")
    input_semantics = _read("docs/reference/input_semantics_ko.md")
    source_adapter = _read("docs/reference/source_adapter_ko.md")
    runtime_contract = _read("docs/reference/runtime_evaluation_contract_ko.md")
    parameter_lab = _read("docs/how-to/parameter_lab_ko.md")
    roadmap = _read("docs/status/roadmap_ko.md")

    assert overview.startswith("# 00. 프로젝트 개요")
    assert principles.startswith("# 01. 운영 원칙")
    assert scope.startswith("# 02. 연구 범위")
    assert foundation.startswith("# 03. Base Field 기초")
    assert input_semantics.startswith("# 04. 입력 Semantics")
    assert source_adapter.startswith("# 05. Source Adapter")
    assert runtime_contract.startswith("# 06. Runtime Contract")
    assert parameter_lab.startswith("# 07. Parameter Lab 사용")
    assert roadmap.startswith("# 08. 로드맵")

    for body in (
        overview,
        principles,
        scope,
        foundation,
        input_semantics,
        source_adapter,
        runtime_contract,
        parameter_lab,
        roadmap,
    ):
        assert "- 역할:" in body
        assert "- 현재성:" in body
        assert "- 대상 독자:" in body
        assert "- 다음으로 읽을 문서:" in body

    assert "whole-space preference field" in overview
    assert "SSC는 canonical truth가 아니다" in overview
    assert "docs/reference/source_adapter_ko.md" in input_semantics
    assert "`SemanticInputSnapshot + QueryContext`" in source_adapter
    assert "toy loader output과 generic source adapter output을 같은 canonical contract로 다룬다" in runtime_contract
    assert "## Prerequisite" in parameter_lab
    assert "## 기본 사용 절차" in parameter_lab
    assert "Phase 5: 완료" in roadmap


def test_reading_docs_are_grouped_merged_and_non_canonical() -> None:
    input_notes = _read("docs/reading/source/input_reconstruction_notes_ko.md")
    phase5_history = _read("docs/reading/history/phase5_adapter_proposal_ko.md")
    external_refs = _read("docs/reading/references/external_references_ko.md")
    archive_refs = _read("docs/reading/history/archive/archive_references_ko.md")
    math_readme = _read("docs/reading/math/README.md")
    current_formula = _read("docs/reference/current_formula_reference_ko.md")

    assert "이 문서는 canonical truth가 아니다" in input_notes
    assert "Semantic Support Conditions" in input_notes
    assert "Input Capability Tiers" in input_notes
    assert "SSC Mapping Example" in input_notes
    assert "docs/reference/input_semantics_ko.md" in input_notes

    assert "이 문서는 canonical truth가 아니다" in phase5_history
    assert "docs/reference/source_adapter_ko.md" in phase5_history
    assert "proposal history / reading 기록" in phase5_history

    assert "이 문서는 canonical truth가 아니다" in external_refs
    assert "docs/explanation/" in external_refs
    assert "docs/reference/" in external_refs
    assert "docs/how-to/" in external_refs

    assert "이 문서는 canonical truth가 아니다" in archive_refs
    assert "../../source/input_reconstruction_notes_ko.md" in archive_refs

    assert "current implementation formula truth는 `docs/reference/current_formula_reference_ko.md`" in math_readme
    assert "## Progression Surface" in current_formula
    assert "## State / Trajectory Composition" in current_formula

    assert not (ROOT / "docs/reading/current_implementation_formula_reference_ko.md").exists()
    assert not (ROOT / "docs/reading/all_formulas_ko.md").exists()
    assert not (ROOT / "docs/reading/input_capability_tiers_ko.md").exists()
    assert not (ROOT / "docs/reading/semantic_support_conditions_ko.md").exists()
    assert not (ROOT / "docs/reading/ssc_input_mapping_ko.md").exists()


def test_internal_and_status_docs_reference_new_ia() -> None:
    project_status = _read("docs/status/project_status_ko.md")
    internal_readme = _read("docs/internal/README.md")
    internal_status = _read("docs/internal/status.md")
    internal_priorities = _read("docs/internal/priorities.md")

    assert "docs/reference/source_adapter_ko.md" in project_status
    assert "docs/reading/history/phase5_adapter_proposal_ko.md" in project_status
    assert "docs/explanation/" in internal_readme
    assert "docs/reference/" in internal_readme
    assert "docs/how-to/" in internal_readme
    assert "docs/explanation/research_scope_ko.md" in internal_readme
    assert "Phase 5 is complete and the repo is in Phase 6 prep state" in internal_status
    assert "Keep Phase 5 results stable" in internal_priorities


def test_markdown_relative_links_resolve() -> None:
    markdown_files = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
    missing: list[str] = []

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            clean_target = target.split("#", 1)[0].strip()
            if not clean_target or "://" in clean_target or clean_target.startswith("mailto:"):
                continue
            if clean_target.startswith("/"):
                resolved = Path(clean_target)
            else:
                resolved = (path.parent / clean_target).resolve()
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {clean_target}")

    assert not missing, "\n".join(missing)
