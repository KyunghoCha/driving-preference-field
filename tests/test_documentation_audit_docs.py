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
    assert "design document" in en
    assert "설계 문서" in ko


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


def test_raw_owner_notes_expand_referential_fragments_with_surrounding_messages() -> None:
    gate_note = _read("docs/raw/notes/2026-03-17-progression-from-geometric-gate-intuition.md")
    segment_note = _read("docs/raw/notes/2026-03-17-segment-index-consumption-and-reachable-progress.md")
    splice_note = _read("docs/raw/notes/2026-03-17-local-splice-and-lane-range.md")
    contract_note = _read("docs/raw/notes/2026-03-17-segment-first-global-path-contract-and-visualization.md")
    frontier_note = _read("docs/raw/notes/2026-03-22-progress-first-node-progression-and-frontier-priority.md")
    semantics_note = _read("docs/raw/notes/2026-04-09-docs-first-reset-and-canonical-semantics.md")
    score_space_note = _read("docs/raw/notes/2026-04-09-progress-tilted-score-space-and-layer-separation.md")
    fabric_note = _read("docs/raw/notes/2026-04-09-whole-space-fabric-instead-of-tube-support.md")
    snapshot_note = _read("docs/raw/notes/2026-04-10-semantic-snapshot-query-context-and-score-function.md")
    progress_note = _read("docs/raw/notes/2026-04-17-dpf-as-progress-preference-device.md")
    weighting_note = _read("docs/raw/notes/2026-04-17-longitudinal-vs-transverse-weighting.md")
    simulator_note = _read("docs/raw/notes/2026-04-18-simulator-comparison-methodology-and-mppi-tuning.md")

    assert "게이트를 지나면 다음 노드로 갈아타는 방식" in gate_note
    assert "게이트 지나면 다음 노드로 가는건 어때" in gate_note
    assert "게이트 지날 때 범위 내에 있으면" in gate_note
    assert "경로에 인덱스를 붙여서 소비" in segment_note
    assert "갈 수 있는 길은 갈 수 있게" in segment_note
    assert "PLEASE IMPLEMENT THIS PLAN" in segment_note
    assert "ego에서 다음 노드까지만 경로를 다시 만드는 방향" in splice_note
    assert "범위는 차선범위" in splice_note
    assert "전역 경로를 생성할 때부터 하나가 아니라 세그먼트들로" in contract_note
    assert "노드랑 간선형태" in contract_note
    assert "PLEASE IMPLEMENT THIS PLAN" in contract_note
    assert "갈 수 있는곳까지 플래닝" in frontier_note
    assert "Frontier-First Blocked Progression" in frontier_note
    assert "문서랑 생각 철학 이런거만 가져가서 새로 만드는게 낫다고" in semantics_note
    assert "선호는 입력이 아니라 field 구조가 생성한다" in semantics_note
    assert "중력장 처럼 돼있는 공간" in score_space_note
    assert "진행방향으로 기울어진 점수 공간" in score_space_note
    assert "선호는 우리가 정하는게 아니라" in score_space_note
    assert "애초에 공간이라니까" in fabric_note
    assert "꽈배기같은걸 생각했단 말이야" in fabric_note
    assert "Tube Field 제거와 Whole-Fabric Progression Space" in fabric_note
    assert "의미번역기만" in snapshot_note
    assert "Semantic Input Snapshot" in snapshot_note
    assert "Query Context" in snapshot_note
    assert "goal cost func" in snapshot_note
    assert "1번은 파라미터로 조정하면 되는거고" in progress_note
    assert "진행방향 성분이 메인으로 가고" in progress_note
    assert "2변은 진행 선호를 주는 장치지" in progress_note
    assert "2변은 진행 선호를 주는 장치지" in weighting_note
    assert "mppi를 얼마나 최적화 할 수 있는지" in simulator_note
    assert "real-time constrained benchmark" in simulator_note


def test_owner_design_notebook_tracks_latest_user_framing() -> None:
    notebook = _read("docs/raw/owner_design_notebook.md")

    for heading in (
        "## DPF가 하는 일",
        "## DPF가 하지 않는 일",
        "## 입력 의미와 layer 분리",
        "## 공간 전체의 점수 구조",
        "## 진행을 읽는 기준과 게이트 직관",
        "## 입력 경로의 역할",
        "## 진행방향 성분과 횡방향 성분",
        "## local evaluation과 Query Context",
        "## planner / behavior와의 책임 경계",
        "## branch, merge, reverse를 보는 관점",
    ):
        assert heading in notebook
    assert "현재 사용자 framing" not in notebook
    assert "관련 raw notes" not in notebook
    assert "현재 열린 쟁점" not in notebook
    assert "메타를 줄인 clean design prose" not in notebook
    assert "reference spine" not in notebook


def test_owner_design_history_tracks_design_evolution() -> None:
    history = _read("docs/raw/owner_design_history.md")

    for heading in (
        "## 문제가 처음 보인 방식",
        "## 게이트 직관과 progression의 출발점",
        "## node 도달보다 consume / 통과를 중시하게 된 흐름",
        "## gate-only 단순화가 흔들린 과정",
        "## docs-first reset과 canonical semantics 재고정",
        "## progress-tilted score space와 layer 분리",
        "## whole-space fabric instead of tube support",
        "## Semantic Snapshot / Query Context / score function 언어",
        "## DPF를 progress-preference device로 읽게 된 전환",
        "## longitudinal와 transverse에 대한 역할 재정의",
        "## planner / behavior와의 책임 경계가 분리된 과정",
        "## 비교 방법론이 설계와 분리된 과정",
        "## 현재 시점의 설계 위치",
    ):
        assert heading in history
    assert "### First raised" not in history
    assert "### Current framing" not in history
    assert "## Source sessions" not in history
    assert "관련 raw notes" not in history
    assert "인덱스를 붙여 consume" in history
    assert "frontier" in history
    assert "ego -> next" in history
    assert "주행 가능 의미 + 진행 의미" in history
    assert "중력장처럼 돼있는 공간" in history
    assert "whole-space fabric" in history
    assert "Semantic Input Snapshot" in history
    assert "진행 선호를 주는 장치" in history
    assert "reference spine" not in history


def test_workflow_guard_mentions_raw_owner_thought_capture() -> None:
    agents = _read("AGENTS.md")
    repo_skill = _read("plugins/dpf-working-rules/skills/dpf-working-rules/SKILL.md")
    home_skill = Path("/home/ckh/.codex/skills/dpf-repo-guard/SKILL.md").read_text(encoding="utf-8")

    for body in (agents, repo_skill, home_skill):
        assert "docs/raw/notes/" in body
        assert "owner_thought_tracker.md" in body
        assert "owner_design_notebook.md" in body
        assert "owner_design_history.md" in body
        assert "repo-level intuition" in body
        assert "clean design prose" in body
        assert "clean design history prose" in body
        assert "current active thread" in body or "current thread" in body
        assert "broader materialized source window" in body
        assert "widen `docs/raw/notes/` first" in body
        assert "PLEASE IMPLEMENT THIS PLAN" in body
        assert "then update `docs/raw/owner_thought_tracker.md`" in body or "then `docs/raw/owner_thought_tracker.md`" in body
