# Docs Audit

이 감사는 `git ls-files 'docs/**'` 기준 tracked 문서 26개를 확인한 결과를 정리한다.
범위는 `docs/index.md`, `docs/design/`, `docs/explanation/`, `docs/reference/`, `docs/how-to/`, `docs/status/`, `docs/reading/`, `docs/internal/` 전체다.

## 현재 역할

문서군은 현재 다음 역할로 나뉜다.

- 포털:
  - `docs/index.md`
- 호환 안내:
  - `docs/design/index.md`
- explanation:
  - `project_overview_ko.md`
  - `engineering_operating_principles_ko.md`
  - `research_scope_ko.md`
  - `base_field_foundation_ko.md`
- reference:
  - `input_semantics_ko.md`
  - `source_adapter_ko.md`
  - `base_field_terms_ko.md`
  - `layer_composition_ko.md`
  - `runtime_evaluation_contract_ko.md`
  - `current_formula_reference_ko.md`
- how-to:
  - `parameter_lab_ko.md`
- status:
  - `roadmap_ko.md`
  - `project_status_ko.md`
  - `experiment_plan_ko.md`
- reading:
  - `history/archive/*`
  - `history/phase5_adapter_proposal_ko.md`
  - `math/README.md`
  - `references/external_references_ko.md`
  - `source/input_reconstruction_notes_ko.md`
- internal:
  - `README.md`
  - `glossary.md`
  - `priorities.md`
  - `status.md`

## 실제 상태

- IA 자체는 현재 일관된다.
  - `docs/index.md`가 포털 역할을 하고,
  - `docs/design/index.md`는 옛 경로가 비어 보이는 혼란을 막는 호환 안내 역할을 한다.
- canonical/current/history 경계도 대체로 유지된다.
  - explanation은 프로젝트 철학과 범위를,
  - reference는 계약과 정의를,
  - how-to는 도구 사용 절차를,
  - reading은 proposal/history/example note를 담는다.
- `current_formula_reference_ko.md`는 이전보다 풍부해졌지만,
  여전히 explanation과 reference의 밀도가 섞여 있다.
- `reading/math/README.md`는 실제 수식 truth가 reference로 이동했다는 점을 설명하지만,
  경로 자체는 빈 디렉토리처럼 보이기 쉽다.
- explanation 문서는 메타 블록을 걷어냈지만,
  `base_field_foundation_ko.md`처럼 문단 밀도가 높은 문서는 사람 가독성이 아직 약하다.
- `docs/index.md`는 포털 역할을 잘 수행하지만,
  newcomer spine, 역할 표, 상태 설명이 한 화면에 많이 모여 있어 여전히 체계 중심으로 읽히는 면이 있다.

## 문제 유형

### 1. explanation 문서의 밀도 편차

- `project_overview_ko.md`는 비교적 읽히는 설명 문서에 가깝다.
- `base_field_foundation_ko.md`는 핵심 개념을 담고 있지만 문단당 주장 수가 많고,
  영문 용어가 잦아 사람이 읽을 때 조밀하게 느껴진다.
- `research_scope_ko.md`는 범위를 잘 고정하지만, 현재 explanation 톤보다 status 톤에 더 가깝게 읽힌다.

### 2. reference 문서의 설명 밀도 편차

- `input_semantics_ko.md`, `source_adapter_ko.md`, `runtime_evaluation_contract_ko.md`는 lookup-first 구조를 지키는 편이다.
- `current_formula_reference_ko.md`는 필요한 설명이 늘어난 대신, reference가 아니라 해설 문서처럼 길어지는 구간이 있다.
- `base_field_terms_ko.md`와 `layer_composition_ko.md`는 현재 reference이지만 일부 설명을 explanation 쪽으로 보내도 된다.

### 3. reading 경계는 유지되지만 체감상 얇거나 두꺼운 문서가 공존

- `phase5_adapter_proposal_ko.md`는 history 문서로 충분하다.
- `input_reconstruction_notes_ko.md`는 source/input 주변 notes를 한곳에 잘 모았지만,
  canonical과 note의 경계 설명이 여전히 약간 반복된다.
- `reading/math/README.md`는 의도적으로 비워 둔 안내문이지만,
  독자는 “math 경로가 사실상 비었다”고 느낄 수 있다.

### 4. internal 문서는 목적이 분명하지만 audit 부재

- `docs/internal/*`는 working vocabulary와 우선순위를 잘 유지하고 있다.
- 다만 이번 감사 전까지는 “전수 감사 결과”를 남기는 고정 경로가 없었다.

## 유지할 것

- `docs/index.md` 중심의 포털 구조
- `docs/design/index.md`를 통한 호환 안내
- explanation / reference / how-to / status / reading / internal 분리
- `Phase 5 완료, Phase 6 준비 상태`를 README, overview, status에서 함께 유지하는 방식
- `SSC는 validation source` 경계
- `SemanticInputSnapshot + QueryContext`, `higher is better`, `FieldRuntime` public contract 같은 핵심 표현의 일관성

## 수정이 필요한 것

- explanation 문서,
  특히 `base_field_foundation_ko.md`의 문단 밀도와 용어 도입 방식을 다시 손봐야 한다.
- `current_formula_reference_ko.md`는 수식 해설을 유지하되,
  lookup-first 구조를 더 선명히 할 필요가 있다.
- `docs/index.md`는 포털 역할을 유지하되,
  한 화면에 겹치는 안내 문장을 더 줄일 여지가 있다.
- `reading/math/README.md`는 현재 상태를 더 분명히 설명하거나,
  math 경로의 기대치를 명시하는 보강이 필요하다.

## 보류할 것

- reading/history 문서의 대규모 압축
- internal 문서의 영어/한국어 재배치
- archive 문서의 추가 정리

## 다음 재작성 우선순위

1. `docs/explanation/*`
2. `docs/reference/*`
3. `docs/how-to/*`
4. `docs/status/*`
5. `docs/reading/*`
6. `docs/internal/*`
