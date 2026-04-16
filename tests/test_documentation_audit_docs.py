from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_documentation_writing_principles_doc_exists_and_links_official_references() -> None:
    body = _read("docs/explanation/documentation_writing_principles_ko.md")

    assert "문서 작성 원칙" in body
    assert "문서의 목적은 독자의 질문에 답하는 것" in body
    assert "한 문단이 답하는 질문을 하나로 유지" in body
    assert "AI가 빠르게 개념과 계약을 복원" in body
    assert "docs/reading/references/documentation_style_references_ko.md" in body


def test_parameter_exposure_policy_doc_exists_and_defines_tiers() -> None:
    body = _read("docs/explanation/parameter_exposure_policy_ko.md")

    assert "파라미터 노출 정책" in body
    assert "`Main`" in body
    assert "`Advanced`" in body
    assert "`Internal`" in body
    assert "Workspace" in body
    assert "Parameters" in body


def test_parameter_catalog_doc_exists_and_lists_main_and_hidden_tunables() -> None:
    body = _read("docs/reference/parameter_catalog_ko.md")

    assert "파라미터 카탈로그" in body
    assert "ProgressionConfig" in body
    assert "_ANCHOR_SPACING_M" in body
    assert "_TRANSVERSE_HANDOFF_TEMPERATURE" in body
    assert "overlay visibility" in body
    assert "_EPS" in body


def test_documentation_style_references_doc_exists_with_official_sources() -> None:
    body = _read("docs/reading/references/documentation_style_references_ko.md")

    assert "Documentation Style References" in body
    assert "https://diataxis.fr/" in body
    assert "https://developers.google.com/tech-writing/one/paragraphs" in body
    assert "https://learn.microsoft.com/en-us/style-guide/welcome/" in body
    assert "https://kubernetes.io/docs/contribute/style/style-guide/" in body
    assert "https://redhat-documentation.github.io/modular-docs/" in body


def test_internal_audit_docs_exist_for_each_file_group() -> None:
    expected = [
        ROOT / "docs/internal/audit/index.md",
        ROOT / "docs/internal/audit/docs_audit_ko.md",
        ROOT / "docs/internal/audit/src_audit_ko.md",
        ROOT / "docs/internal/audit/tests_audit_ko.md",
        ROOT / "docs/internal/audit/root_audit_ko.md",
    ]

    for path in expected:
        assert path.exists(), str(path.relative_to(ROOT))


def test_audit_docs_record_repo_tracked_scope_and_next_order() -> None:
    docs_audit = _read("docs/internal/audit/docs_audit_ko.md")
    src_audit = _read("docs/internal/audit/src_audit_ko.md")
    tests_audit = _read("docs/internal/audit/tests_audit_ko.md")
    root_audit = _read("docs/internal/audit/root_audit_ko.md")
    audit_index = _read("docs/internal/audit/index.md")

    assert "tracked 문서 26개" in docs_audit
    assert "tracked source 파일 34개" in src_audit
    assert "tracked test 파일 14개" in tests_audit
    assert "Root-level tracked files 7개" in root_audit
    assert "1. `docs/explanation/*`" in audit_index
    assert "7. public-facing `src` 주석 / CLI help / docstring" in audit_index
