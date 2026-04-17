from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+.+$", re.MULTILINE)
PUBLIC_DOC_DIRS = ("explanation", "reference", "how-to", "status")


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _tree_files(language: str) -> list[str]:
    base = ROOT / "docs" / language
    return sorted(str(path.relative_to(base)) for path in base.rglob("*.md"))


def _public_tree_files(language: str) -> list[str]:
    base = ROOT / "docs" / language
    return sorted(
        str(path.relative_to(base))
        for directory in PUBLIC_DOC_DIRS
        for path in sorted((base / directory).rglob("*.md"))
    )


def _heading_depths(path: Path) -> list[int]:
    return [len(match.group(1)) for match in HEADING_PATTERN.finditer(path.read_text(encoding="utf-8"))]


def test_docs_trees_have_identical_file_sets() -> None:
    assert _tree_files("en") == _tree_files("ko")


def test_public_docs_have_matching_heading_skeletons() -> None:
    for relpath in _public_tree_files("en"):
        en_path = ROOT / "docs" / "en" / relpath
        ko_path = ROOT / "docs" / "ko" / relpath
        assert _heading_depths(en_path) == _heading_depths(ko_path), relpath


def test_readmes_cross_link_and_point_to_language_portals() -> None:
    readme_en = _read("README.md")
    readme_ko = _read("README.ko.md")

    assert "./README.ko.md" in readme_en
    assert "./README.md" in readme_ko
    assert "./docs/index.md" in readme_en
    assert "./docs/index.md" in readme_ko
    assert "./docs/en/index.md" in readme_en
    assert "./docs/ko/index.md" in readme_en
    assert "./docs/en/index.md" in readme_ko
    assert "./docs/ko/index.md" in readme_ko
    assert "Phase 5 complete, Phase 6 preparation" in readme_en
    assert "Phase 5 완료, Phase 6 준비" in readme_ko


def test_readmes_keep_matching_section_order() -> None:
    heading_pairs = (
        ("## Prerequisites", "## 준비 사항"),
        ("## Quick Start", "## 빠른 시작"),
        ("## Docs", "## 문서"),
        ("## Current Scope", "## 현재 범위"),
    )
    readme_en = _read("README.md")
    readme_ko = _read("README.ko.md")

    previous_en = -1
    previous_ko = -1
    for heading_en, heading_ko in heading_pairs:
        current_en = readme_en.index(heading_en)
        current_ko = readme_ko.index(heading_ko)
        assert current_en > previous_en
        assert current_ko > previous_ko
        previous_en = current_en
        previous_ko = current_ko


def test_docs_index_is_language_landing_page() -> None:
    docs_index = _read("docs/index.md")
    design_index = _read("docs/design/index.md")

    assert "English Docs" in docs_index
    assert "한국어 문서" in docs_index
    assert "./en/index.md" in docs_index
    assert "./ko/index.md" in docs_index
    assert "../index.md" in design_index
    assert "../en/index.md" in design_index
    assert "../ko/index.md" in design_index


def test_raw_owner_thought_surface_is_linked_and_noncanonical() -> None:
    raw_readme = _read("docs/raw/README.md")
    raw_tracker = _read("docs/raw/owner_thought_tracker.md")
    raw_notebook = _read("docs/raw/owner_design_notebook.md")
    en_index = _read("docs/en/index.md")
    ko_index = _read("docs/ko/index.md")

    assert "non-canonical" in raw_readme
    assert "사용자 원문" in raw_readme
    assert "./owner_thought_tracker.md" in raw_readme
    assert "./owner_design_notebook.md" in raw_readme
    assert "./notes/2026-04-17-longitudinal-vs-transverse-weighting.md" in raw_readme
    assert "./notes/2026-04-17-dpf-as-progress-preference-device.md" in raw_readme
    assert "./notes/2026-04-17-raw-thought-capture-workflow.md" in raw_readme
    assert "../raw/README.md" in en_index
    assert "../raw/README.md" in ko_index
    assert "owner design notebook" in en_index
    assert "최신 설계 정리" in ko_index
    assert "Current status" in raw_tracker
    assert "Owner Design Notebook" in raw_notebook


def test_language_portals_expose_same_spine() -> None:
    en_index = _read("docs/en/index.md")
    ko_index = _read("docs/ko/index.md")

    expected_relative_paths = (
        "./explanation/project_overview.md",
        "./explanation/engineering_operating_principles.md",
        "./reference/source_adapter.md",
        "./reference/runtime_evaluation_contract.md",
        "./how-to/parameter_lab.md",
        "./status/roadmap.md",
    )
    for target in expected_relative_paths:
        assert target in en_index
        assert target in ko_index
    assert "Newcomer Spine" in en_index
    assert "처음 읽는 순서" in ko_index


def test_key_truths_survive_in_both_languages() -> None:
    overview_en = _read("docs/en/explanation/project_overview.md")
    overview_ko = _read("docs/ko/explanation/project_overview.md")
    guide_en = _read("docs/en/how-to/parameter_lab.md")
    guide_ko = _read("docs/ko/how-to/parameter_lab.md")
    runtime_en = _read("docs/en/reference/runtime_evaluation_contract.md")
    runtime_ko = _read("docs/ko/reference/runtime_evaluation_contract.md")

    assert "whole-space preference field" in overview_en
    assert "whole-space preference field" in overview_ko
    assert "Phase 5 complete, Phase 6 preparation" in overview_en
    assert "Phase 5 완료, Phase 6 준비 상태" in overview_ko
    assert "Start here" in guide_en
    assert "먼저 여기서 시작" in guide_ko
    assert "Quick actions" in guide_en
    assert "빠른 액션" in guide_ko
    assert "How to read the screen" in guide_en
    assert "화면 읽기" in guide_ko
    assert "higher is better" in runtime_en
    assert "higher is better" in runtime_ko


def test_markdown_relative_links_resolve_across_bilingual_docs() -> None:
    markdown_files = [
        ROOT / "README.md",
        ROOT / "README.ko.md",
        ROOT / "docs/index.md",
        ROOT / "docs/design/index.md",
        *sorted((ROOT / "docs" / "raw").rglob("*.md")),
        *sorted((ROOT / "docs" / "en").rglob("*.md")),
        *sorted((ROOT / "docs" / "ko").rglob("*.md")),
    ]
    missing: list[str] = []

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            clean_target = target.split("#", 1)[0].strip()
            if not clean_target or "://" in clean_target or clean_target.startswith("mailto:"):
                continue
            resolved = (path.parent / clean_target).resolve() if not clean_target.startswith("/") else Path(clean_target)
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {clean_target}")

    assert not missing, "\n".join(missing)
