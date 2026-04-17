# 문서 인덱스

`driving-preference-field`의 한국어 문서 포털이다. 현재 프로젝트 상태는 `Phase 5 완료, Phase 6 준비 상태`다.

## AI workflow

이 repo에는 AI/Codex 작업용 workflow guard가 있다. agent-facing file은 영문 [../../AGENTS.md](../../AGENTS.md)와 [../../plugins/dpf-working-rules/](../../plugins/dpf-working-rules/) 아래만 유지한다.

## 처음 읽는 순서

1. [프로젝트 개요](./explanation/project_overview.md)
2. [운영 원칙](./explanation/engineering_operating_principles.md)
3. [연구 범위](./explanation/research_scope.md)
4. [Base Field 기초](./explanation/base_field_foundation.md)
5. [입력 의미 계약](./reference/input_semantics.md)
6. [소스 어댑터](./reference/source_adapter.md)
7. [런타임 계약](./reference/runtime_evaluation_contract.md)
8. [Parameter Lab 사용](./how-to/parameter_lab.md)
9. [로드맵](./status/roadmap.md)

## 설명

| 문서 | 역할 | 언제 읽는지 |
| --- | --- | --- |
| [프로젝트 개요](./explanation/project_overview.md) | 프로젝트 목적 | 처음 들어올 때 |
| [운영 원칙](./explanation/engineering_operating_principles.md) | repo 운영 기준과 기본 휴리스틱 | 코드, 문서, 실험 방향을 바꾸기 전에 |
| [문서 작성 원칙](./explanation/documentation_writing_principles.md) | 문서 작성 기준 | 문서를 다시 쓸 때 |
| [파라미터 노출 정책](./explanation/parameter_exposure_policy.md) | knob 노출 기준 | 새 control을 추가하거나 숨기기 전에 |
| [연구 범위](./explanation/research_scope.md) | 범위 경계 | claim을 넓히기 전에 |
| [Base Field 기초](./explanation/base_field_foundation.md) | Base Field 개념 | progression semantics를 건드리기 전에 |

## 레퍼런스

| 문서 | 역할 | 언제 읽는지 |
| --- | --- | --- |
| [입력 의미 계약](./reference/input_semantics.md) | canonical 입력 구조 | 입력 계약을 바꾸기 전에 |
| [소스 어댑터](./reference/source_adapter.md) | adapter 출력 계약 | loader/adapter를 바꾸기 전에 |
| [Base Field 항](./reference/base_field_terms.md) | Base Field 항 구분 | layer 의미를 바꾸기 전에 |
| [Layer 조합](./reference/layer_composition.md) | layer 조합 규칙 | runtime composition을 바꾸기 전에 |
| [파라미터 카탈로그](./reference/parameter_catalog.md) | 현재 knob와 숨겨진 tunable | 새 파라미터를 노출하기 전에 |
| [런타임 계약](./reference/runtime_evaluation_contract.md) | runtime API 계약 | public runtime behavior를 바꾸기 전에 |
| [현재 구현 수식](./reference/current_formula_reference.md) | 현재 구현 수식 | 현재 수식이 필요할 때 |

## 사용 방법

| 문서 | 역할 | 언제 읽는지 |
| --- | --- | --- |
| [Parameter Lab 사용](./how-to/parameter_lab.md) | 도구 사용 흐름 | Lab을 실행하고 읽을 때 |

## 상태

| 문서 | 역할 | 언제 읽는지 |
| --- | --- | --- |
| [로드맵](./status/roadmap.md) | phase truth | 현재 phase와 다음 단계를 볼 때 |
| [진행 상태](./status/project_status.md) | current snapshot | 최근 완료 작업을 확인할 때 |
| [실험 계획](./status/experiment_plan.md) | 실험 실행과 비교 discipline | 실험을 시작하거나 기록하거나 리뷰하기 전에 |

## 읽을거리

| 문서 | 역할 | 언제 읽는지 |
| --- | --- | --- |
| [입력 재구성 메모](./reading/source/input_reconstruction_notes.md) | 비-canonical 메모 | input/source 예시를 참고할 때 |
| [Phase 5 Adapter 제안 이력](./reading/history/phase5_adapter_proposal.md) | 제안 이력 | 예전 adapter 논의를 추적할 때 |
| [외부 참고 자료](./reading/references/external_references.md) | 외부 참고 로그 | 외부 근거를 다시 확인할 때 |
| [문서 스타일 참고 자료](./reading/references/documentation_style_references.md) | 공식 글쓰기 참고 | 문서 스타일 기준을 다시 볼 때 |
| [사용자 raw 기록](../raw/README.md) | 사용자 thought raw 기록, 변화 추적, 최신 설계 문서 | 사용자 원문 생각, 변화 기록, 최신 사용자 설계 thinking을 참고하되 canonical truth로 읽지 않을 때 |
| [Archive 참고 자료](./reading/history/archive/archive_references.md) | archive 위치 안내 | archive 메모 위치를 찾을 때 |
| [Archive score field 메모](./reading/history/archive/archive_score_field_notes.md) | archive 메모 | 과거 메모를 추적할 때 |

## 내부 문서

| 문서 | 역할 | 언제 읽는지 |
| --- | --- | --- |
| [내부 문서 안내](./internal/README.md) | internal 경계 | internal note를 추가하기 전에 |
| [감사 인덱스](./internal/audit/index.md) | audit 시작점 | 파일군별 감사 결과를 볼 때 |
| [내부 상태](./internal/status.md) | internal snapshot | maintainer용 상태를 복기할 때 |
| [내부 우선순위](./internal/priorities.md) | internal 우선순위 | cleanup 우선순위를 볼 때 |
| [내부 용어집](./internal/glossary.md) | internal 용어 기준 | 용어 drift를 맞출 때 |
