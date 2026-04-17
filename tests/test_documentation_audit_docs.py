from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
PUBLIC_DOC_DIRS = ("explanation", "reference", "how-to", "status")


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_writing_principles_exist_in_both_languages() -> None:
    en = _read("docs/en/explanation/documentation_writing_principles.md")
    ko = _read("docs/ko/explanation/documentation_writing_principles.md")

    assert "documentation exists to answer a question" in en
    assert "문서의 목적은 독자의 질문에 답하는 것" in ko
    assert "documentation_style_references.md" in en
    assert "documentation_style_references.md" in ko
    assert "`docs/raw/`" in en
    assert "`docs/raw/`" in ko


def test_parameter_exposure_policy_and_catalog_exist_in_both_languages() -> None:
    policy_en = _read("docs/en/explanation/parameter_exposure_policy.md")
    policy_ko = _read("docs/ko/explanation/parameter_exposure_policy.md")
    catalog_en = _read("docs/en/reference/parameter_catalog.md")
    catalog_ko = _read("docs/ko/reference/parameter_catalog.md")

    for body in (policy_en, policy_ko):
        assert "`Main`" in body
        assert "`Advanced`" in body
        assert "`Internal`" in body
    for body in (catalog_en, catalog_ko):
        assert "anchor_spacing" in body or "anchor_spacing_m" in body
        assert "transverse_handoff_temperature" in body


def test_documentation_style_reference_pages_keep_official_sources() -> None:
    en = _read("docs/en/reading/references/documentation_style_references.md")
    ko = _read("docs/ko/reading/references/documentation_style_references.md")
    urls = (
        "https://diataxis.fr/",
        "https://developers.google.com/tech-writing/one/paragraphs",
        "https://learn.microsoft.com/en-us/style-guide/welcome/",
        "https://kubernetes.io/docs/contribute/style/style-guide/",
        "https://redhat-documentation.github.io/modular-docs/",
    )
    for url in urls:
        assert url in en
        assert url in ko


def test_internal_audit_docs_exist_in_both_languages() -> None:
    audit_relpaths = [
        "internal/audit/index.md",
        "internal/audit/docs_audit.md",
        "internal/audit/src_audit.md",
        "internal/audit/tests_audit.md",
        "internal/audit/root_audit.md",
    ]
    for language in ("en", "ko"):
        for relpath in audit_relpaths:
            assert (ROOT / "docs" / language / relpath).exists(), f"{language}/{relpath}"


def test_audit_index_records_new_bilingual_family_order() -> None:
    en_index = _read("docs/en/internal/audit/index.md")
    ko_index = _read("docs/ko/internal/audit/index.md")

    assert "1. `docs/en/*` and `docs/ko/*`" in en_index
    assert "1." in ko_index


def test_korean_public_docs_do_not_keep_known_awkward_residue() -> None:
    public_roots = [
        ROOT / "docs" / "ko" / "explanation",
        ROOT / "docs" / "ko" / "reference",
        ROOT / "docs" / "ko" / "how-to",
        ROOT / "docs" / "ko" / "status",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for root in public_roots for path in sorted(root.rglob("*.md")))
    forbidden = (
        "## field 의미",
        "## canonical 출력",
        "## inspection 경로",
        "## progression surface",
        "### guide-local anchor 좌표",
        "### guide-local Gaussian weight",
        "### guide-local 좌표",
        "### guide-local longitudinal frame",
        "### secondary modulation",
        "## exception layer",
        "## Optional semantic slot",
        "찾아보기 중심로",
        "known-good NumPy pin",
    )
    for token in forbidden:
        assert token not in combined


def test_korean_public_docs_keep_mixed_terms_in_inline_product_labels() -> None:
    forbidden_inline_labels = {
        "가이드",
        "파라미터 도움말",
        "메인",
        "프로파일",
        "기준",
        "후보",
        "차이",
        "채널",
        "스케일",
    }
    violations: list[str] = []
    for directory in PUBLIC_DOC_DIRS:
        for path in sorted((ROOT / "docs" / "ko" / directory).rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for label in INLINE_CODE_PATTERN.findall(text):
                if label in forbidden_inline_labels:
                    violations.append(f"{path.relative_to(ROOT)} -> `{label}`")

    assert not violations, "\n".join(violations)


def test_raw_owner_notes_follow_expected_template() -> None:
    notes = sorted((ROOT / "docs" / "raw" / "notes").glob("*.md"))
    assert notes
    required_headings = (
        "## Date",
        "## Topic",
        "## Source sessions",
        "## User original messages",
        "## Open questions at the time",
    )
    for path in notes:
        text = path.read_text(encoding="utf-8")
        for heading in required_headings:
            assert heading in text, f"{path.relative_to(ROOT)} missing {heading}"


def test_workflow_guard_mentions_raw_owner_thought_capture() -> None:
    agents = _read("AGENTS.md")
    repo_skill = _read("plugins/dpf-working-rules/skills/dpf-working-rules/SKILL.md")

    for body in (agents, repo_skill):
        assert "docs/raw/" in body
        assert "repo-level intuition" in body
