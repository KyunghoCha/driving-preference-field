from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _tree_files(language: str) -> list[str]:
    base = ROOT / "docs" / language
    return sorted(str(path.relative_to(base)) for path in base.rglob("*.md"))


def test_docs_trees_have_identical_file_sets() -> None:
    assert _tree_files("en") == _tree_files("ko")


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
    assert "Quick start" in guide_en
    assert "빠른 시작" in guide_ko
    assert "Guide vs Parameter Help" in guide_en
    assert "`Guide`와 `Parameter Help`의 차이" in guide_ko
    assert "higher is better" in runtime_en
    assert "higher is better" in runtime_ko


def test_markdown_relative_links_resolve_across_bilingual_docs() -> None:
    markdown_files = [
        ROOT / "README.md",
        ROOT / "README.ko.md",
        ROOT / "docs/index.md",
        ROOT / "docs/design/index.md",
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
