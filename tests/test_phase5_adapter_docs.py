from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

ACTIVE_DOCS = [
    "README.md",
    "docs/index.md",
    "docs/design/index.md",
    "docs/explanation/project_overview_ko.md",
    "docs/explanation/engineering_operating_principles_ko.md",
    "docs/explanation/documentation_writing_principles_ko.md",
    "docs/explanation/research_scope_ko.md",
    "docs/explanation/base_field_foundation_ko.md",
    "docs/reference/input_semantics_ko.md",
    "docs/reference/source_adapter_ko.md",
    "docs/reference/base_field_terms_ko.md",
    "docs/reference/layer_composition_ko.md",
    "docs/reference/runtime_evaluation_contract_ko.md",
    "docs/reference/current_formula_reference_ko.md",
    "docs/how-to/parameter_lab_ko.md",
    "docs/status/roadmap_ko.md",
    "docs/status/project_status_ko.md",
    "docs/status/experiment_plan_ko.md",
    "docs/reading/source/input_reconstruction_notes_ko.md",
    "docs/reading/history/phase5_adapter_proposal_ko.md",
    "docs/reading/references/external_references_ko.md",
    "docs/internal/README.md",
    "docs/internal/status.md",
    "docs/internal/priorities.md",
    "docs/internal/glossary.md",
]

TITLE_DOCS = [
    "docs/explanation/project_overview_ko.md",
    "docs/explanation/engineering_operating_principles_ko.md",
    "docs/explanation/documentation_writing_principles_ko.md",
    "docs/explanation/research_scope_ko.md",
    "docs/explanation/base_field_foundation_ko.md",
    "docs/reference/input_semantics_ko.md",
    "docs/reference/source_adapter_ko.md",
    "docs/reference/runtime_evaluation_contract_ko.md",
    "docs/how-to/parameter_lab_ko.md",
    "docs/status/roadmap_ko.md",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_stays_short_landing_page() -> None:
    readme = _read("README.md")
    docs_index = _read("docs/index.md")

    assert "Phase 5 완료, Phase 6 준비 상태" in readme
    assert "docs/index.md" in readme
    assert "docs/explanation/project_overview_ko.md" in readme
    assert "docs/reference/source_adapter_ko.md" in readme
    assert "docs/reference/current_formula_reference_ko.md" in readme
    assert "## Explanation" not in readme
    assert "## Reference" not in readme
    assert "## Newcomer Spine" not in readme
    assert len(readme.splitlines()) < len(docs_index.splitlines())


def test_docs_index_stays_portal_with_newcomer_spine() -> None:
    docs_index = _read("docs/index.md")
    design_index = _read("docs/design/index.md")

    assert "Phase 5 완료, Phase 6 준비 상태" in docs_index
    assert "## Newcomer Spine" in docs_index
    assert "1. [00. 프로젝트 개요]" in docs_index
    assert "./design/index.md" in docs_index
    assert "./explanation/project_overview_ko.md" in docs_index
    assert "./explanation/documentation_writing_principles_ko.md" in docs_index
    assert "./reference/source_adapter_ko.md" in docs_index
    assert "./how-to/parameter_lab_ko.md" in docs_index
    assert "./reading/source/input_reconstruction_notes_ko.md" in docs_index
    assert "./reading/history/phase5_adapter_proposal_ko.md" in docs_index
    assert "./reading/references/external_references_ko.md" in docs_index
    assert "./reading/references/documentation_style_references_ko.md" in docs_index
    assert "./internal/audit/index.md" in docs_index
    assert "| 문서 | canonical | 대상 독자 | 언제 읽는지 |" in docs_index
    assert "../explanation/project_overview_ko.md" in design_index
    assert "../explanation/documentation_writing_principles_ko.md" in design_index
    assert "../reference/runtime_evaluation_contract_ko.md" in design_index
    assert "../how-to/parameter_lab_ko.md" in design_index


def test_active_docs_no_visible_metadata_blocks() -> None:
    forbidden_fragments = (
        "- 역할:",
        "- 현재성:",
        "- 대상 독자:",
        "- 다음으로 읽을 문서:",
        "## 문서 목적",
    )

    for path in ACTIVE_DOCS:
        body = _read(path)
        for fragment in forbidden_fragments:
            assert fragment not in body, f"{path} still contains {fragment!r}"


def test_individual_doc_titles_are_not_numbered() -> None:
    for path in TITLE_DOCS:
        first_line = _read(path).splitlines()[0]
        assert re.match(r"# (?![0-9]{2}\\.)", first_line), f"{path} still uses numbered H1"


def test_key_truths_remain_after_rewrite() -> None:
    overview = _read("docs/explanation/project_overview_ko.md")
    foundation = _read("docs/explanation/base_field_foundation_ko.md")
    source_adapter = _read("docs/reference/source_adapter_ko.md")
    runtime_contract = _read("docs/reference/runtime_evaluation_contract_ko.md")
    formula_reference = _read("docs/reference/current_formula_reference_ko.md")
    project_status = _read("docs/status/project_status_ko.md")

    assert "whole-space preference field" in overview
    assert "SSC는 이 아이디어를 실제로 검증하는 중요한 downstream validation source다." in overview
    assert "Phase 5 완료, Phase 6 준비 상태" in overview
    assert "higher is better" in foundation
    assert "`SemanticInputSnapshot + QueryContext`" in source_adapter
    assert "FieldRuntime.query_state(state)" in runtime_contract
    assert "toy loader output과 generic source adapter output" in runtime_contract
    assert "higher is better" in runtime_contract
    assert "## 이 문서를 읽는 방법" in formula_reference
    assert "왜 이 수식이 필요한가" in formula_reference
    assert "Phase 5 완료, Phase 6 준비 상태" in project_status


def test_parameter_lab_doc_is_procedural() -> None:
    parameter_lab = _read("docs/how-to/parameter_lab_ko.md")

    assert "## Prerequisite" in parameter_lab
    assert "## 실행" in parameter_lab
    assert "## baseline/candidate 비교 절차" in parameter_lab
    assert "## Export 결과물" in parameter_lab
    assert "## 현재 제한사항" in parameter_lab
    assert "geometry 편집" in parameter_lab
    assert "Apply" in parameter_lab


def test_reading_docs_keep_short_non_canonical_banner() -> None:
    input_notes = _read("docs/reading/source/input_reconstruction_notes_ko.md")
    phase5_history = _read("docs/reading/history/phase5_adapter_proposal_ko.md")
    external_refs = _read("docs/reading/references/external_references_ko.md")
    input_head = "\n".join(input_notes.splitlines()[:5])
    history_head = "\n".join(phase5_history.splitlines()[:5])

    assert input_notes.splitlines()[2].startswith("> ")
    assert phase5_history.splitlines()[2].startswith("> ")
    assert external_refs.splitlines()[2].startswith("> ")
    assert "Semantic Support Conditions" in input_notes
    assert "SSC Mapping Example" in input_notes
    assert "현재 상태: reading" not in input_head
    assert "proposal history / reading 기록" not in history_head


def test_internal_and_status_docs_reference_new_ia() -> None:
    internal_readme = _read("docs/internal/README.md")
    internal_status = _read("docs/internal/status.md")
    internal_priorities = _read("docs/internal/priorities.md")
    roadmap = _read("docs/status/roadmap_ko.md")

    assert "docs/explanation/" in internal_readme
    assert "docs/reference/" in internal_readme
    assert "docs/how-to/" in internal_readme
    assert "Phase 5 is complete and the repo is in Phase 6 prep state" in internal_status
    assert "Keep Phase 5 results stable" in internal_priorities
    assert "Phase 5 완료, Phase 6 준비 상태" in roadmap
    assert "### Phase 5. Source Adapter" in roadmap


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
