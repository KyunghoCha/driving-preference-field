# 문서 인덱스

이 워크스페이스는 문서 SSOT를 먼저 세우고, 그 위에 evaluator와 Parameter Lab을 단계적으로 구현하는 프로젝트다.

현재 문서 상태는 `Phase 5 완료, Phase 6 준비 상태`다.

처음 보는 사람은 아래 순서로 읽는 것이 가장 빠르다.

1. [프로젝트 개요](./design/project_overview_ko.md)
2. [운영 원칙](./design/engineering_operating_principles_ko.md)
3. [Base Field 기초](./design/base_field_foundation_ko.md)
4. [Source Adapter](./design/source_adapter_ko.md)
5. [Runtime Evaluation Contract](./design/runtime_evaluation_contract_ko.md)
6. [로드맵](./status/roadmap_ko.md)

## Canonical

- [프로젝트 개요](./design/project_overview_ko.md)
- [운영 원칙](./design/engineering_operating_principles_ko.md)
- [연구 범위](./design/research_scope_ko.md)
- [Base Field 기초](./design/base_field_foundation_ko.md)
- [입력 Semantics](./design/input_semantics_ko.md)
- [Source Adapter](./design/source_adapter_ko.md)
- [Base Field 항](./design/base_field_terms_ko.md)
- [Layer 조합](./design/layer_composition_ko.md)
- [Runtime Evaluation Contract](./design/runtime_evaluation_contract_ko.md)
- [Parameter Lab 설계](./design/parameter_lab_ko.md)

## Current Implementation / Status

- [로드맵](./status/roadmap_ko.md)
- [진행 상태](./status/project_status_ko.md)
- [실험 계획](./status/experiment_plan_ko.md)

## 참고 원칙

- canonical 문서는 현재 정의만 직접 설명한다
- canonical progression field는 source-agnostic하다
- newcomer overview도 canonical 문서로 취급한다
- progression field는 local map 전체에서 longitudinal term과 transverse term을 함께 가진다
- progression semantics와 drivable semantics는 구분해서 본다
- field는 공간의 ordering을 알려주고, winner 방향 선택은 상위 layer가 한다
- canonical score는 higher is better로 읽는다
- archive와 source 예시는 `docs/reading/`에서만 다룬다
- 구현은 문서 SSOT를 기준으로만 확장한다
- Phase 5 current truth는 design SSOT에 있다
- Phase 5 proposal은 reading/history로만 남긴다

## 권장 읽기 순서

1. [프로젝트 개요](./design/project_overview_ko.md)
2. [운영 원칙](./design/engineering_operating_principles_ko.md)
3. [연구 범위](./design/research_scope_ko.md)
4. [Base Field 기초](./design/base_field_foundation_ko.md)
5. [입력 Semantics](./design/input_semantics_ko.md)
6. [Source Adapter](./design/source_adapter_ko.md)
7. [Base Field 항](./design/base_field_terms_ko.md)
8. [Runtime Evaluation Contract](./design/runtime_evaluation_contract_ko.md)
9. [Parameter Lab 설계](./design/parameter_lab_ko.md)
10. [로드맵](./status/roadmap_ko.md)
11. [진행 상태](./status/project_status_ko.md)
12. [실험 계획](./status/experiment_plan_ko.md)

## Reading / Proposal / History

- [외부 참고 문헌 기록](./reading/external_references_ko.md)
- [Current Implementation Formula Reference](./reading/current_implementation_formula_reference_ko.md)
- [입력 Capability Tier](./reading/input_capability_tiers_ko.md)
- [Phase 5 Adapter Proposal History](./reading/phase5_adapter_proposal_ko.md)
- [Archive 참고 목록](./reading/archive_references_ko.md)
- [SSC 입력 매핑](./reading/ssc_input_mapping_ko.md)
- [Archive score field 메모](./reading/archive_score_field_notes_ko.md)

## Internal

- [internal README](./internal/README.md)
- [internal status](./internal/status.md)
- [internal priorities](./internal/priorities.md)
- [internal glossary](./internal/glossary.md)
