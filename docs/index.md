# 문서 인덱스

`driving-preference-field`의 전체 문서 포털이다. 현재 상태는 `Phase 5 완료, Phase 6 준비 상태`이며, 아래 순서로 읽으면 프로젝트의 핵심 개념과 현재 구현 계약을 빠르게 따라갈 수 있다. 예전 `docs/design/` 경로를 찾는 경우에는 [design 안내](./design/index.md)를 먼저 보면 된다.

## Newcomer Spine

1. [00. 프로젝트 개요](./explanation/project_overview_ko.md)
2. [01. 운영 원칙](./explanation/engineering_operating_principles_ko.md)
3. [02. 연구 범위](./explanation/research_scope_ko.md)
4. [03. Base Field 기초](./explanation/base_field_foundation_ko.md)
5. [04. 입력 Semantics](./reference/input_semantics_ko.md)
6. [05. Source Adapter](./reference/source_adapter_ko.md)
7. [06. Runtime Contract](./reference/runtime_evaluation_contract_ko.md)
8. [07. Parameter Lab 사용](./how-to/parameter_lab_ko.md)
9. [08. 로드맵](./status/roadmap_ko.md)

## Explanation

| 문서 | canonical | 대상 독자 | 언제 읽는지 |
| --- | --- | --- | --- |
| [프로젝트 개요](./explanation/project_overview_ko.md) | 예 | newcomer | 프로젝트가 무엇인지 처음 파악할 때 |
| [운영 원칙](./explanation/engineering_operating_principles_ko.md) | 예 | contributor, maintainer | 문서/코드/reading 경계를 잡을 때 |
| [연구 범위](./explanation/research_scope_ko.md) | 예 | newcomer, contributor | in/out of scope를 확인할 때 |
| [Base Field 기초](./explanation/base_field_foundation_ko.md) | 예 | newcomer, contributor | whole-space field 개념을 이해할 때 |

## Reference

| 문서 | canonical/current | 대상 독자 | 언제 읽는지 |
| --- | --- | --- | --- |
| [입력 Semantics](./reference/input_semantics_ko.md) | canonical | contributor | semantic slot 정의를 확인할 때 |
| [Source Adapter](./reference/source_adapter_ko.md) | canonical | contributor | adapter output contract를 확인할 때 |
| [Base Field 항](./reference/base_field_terms_ko.md) | canonical | contributor | 용어와 항 구성을 볼 때 |
| [Layer 조합](./reference/layer_composition_ko.md) | canonical | contributor | base/exception 조합 규칙을 볼 때 |
| [Runtime Contract](./reference/runtime_evaluation_contract_ko.md) | canonical | contributor, maintainer | runtime API와 evaluator 계약을 볼 때 |
| [Current Formula Reference](./reference/current_formula_reference_ko.md) | current implementation | contributor, maintainer | 현재 구현 수식을 대조할 때 |

## How-to

| 문서 | canonical/current | 대상 독자 | 언제 읽는지 |
| --- | --- | --- | --- |
| [Parameter Lab 사용](./how-to/parameter_lab_ko.md) | current implementation | newcomer, contributor | Lab을 실행하고 비교 실험할 때 |

## Status

| 문서 | 역할 | 대상 독자 | 언제 읽는지 |
| --- | --- | --- | --- |
| [로드맵](./status/roadmap_ko.md) | phase truth | newcomer, contributor | 현재 phase와 다음 단계를 볼 때 |
| [진행 상태](./status/project_status_ko.md) | current snapshot | contributor | 완료된 작업과 현재 focus를 볼 때 |
| [실험 계획](./status/experiment_plan_ko.md) | experiment procedure | contributor | morphology 비교 절차를 볼 때 |

## Reading

| 문서 | canonical 여부 | 대상 독자 | 언제 읽는지 |
| --- | --- | --- | --- |
| [Input Reconstruction Notes](./reading/source/input_reconstruction_notes_ko.md) | 비-canonical | contributor | source/input 사례를 참고할 때 |
| [Phase 5 Adapter Proposal History](./reading/history/phase5_adapter_proposal_ko.md) | 비-canonical | maintainer | proposal history를 볼 때 |
| [External References](./reading/references/external_references_ko.md) | 비-canonical | contributor | 참고 문헌 근거를 추적할 때 |
| [Archive References](./reading/history/archive/archive_references_ko.md) | 비-canonical | maintainer | archive 경로를 추적할 때 |
| [Archive Score Field Notes](./reading/history/archive/archive_score_field_notes_ko.md) | 비-canonical | maintainer | 이전 실험 메모를 추적할 때 |

## Internal

| 문서 | 역할 | 대상 독자 | 언제 읽는지 |
| --- | --- | --- | --- |
| [internal README](./internal/README.md) | internal policy | maintainer | internal docs 경계를 확인할 때 |
| [internal status](./internal/status.md) | internal snapshot | maintainer | 내부 상태를 짧게 복기할 때 |
| [internal priorities](./internal/priorities.md) | internal priorities | maintainer | 현재 유지 우선순위를 볼 때 |
| [internal glossary](./internal/glossary.md) | internal terms | maintainer | working vocabulary를 맞출 때 |
