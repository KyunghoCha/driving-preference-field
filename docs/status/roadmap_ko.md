# 프로젝트 로드맵 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 `driving-preference-field`의 전체 진행 단계를 phase 기준으로 정리한다.

이 문서는 다음을 한 곳에서 관리한다.

- 현재 프로젝트가 어느 phase에 있는가
- 각 phase의 목표가 무엇인가
- 다음 phase로 넘어가기 위한 완료 기준이 무엇인가
- 지금 당장 우선순위가 어디에 있는가

## 현재 위치

현재 프로젝트는 **Phase 4 완료, Phase 5 준비 상태**로 본다.

- Phase 0: 완료
- Phase 1: 완료
- Phase 2: 완료
- Phase 3: 완료
- Phase 4: 완료
- Phase 5: 후속 단계

## Phase 구조

### Phase 0. Canonical 문서 정립

목표:

- 프로젝트 범위와 비범위를 고정한다
- 입력 semantics, base field, layer composition, runtime contract를 문서 SSOT로 고정한다
- canonical 문서가 과거 문서나 특정 구현체에 기대지 않도록 정리한다

완료 기준:

- `docs/design/` 핵심 문서가 서로 충돌하지 않는다
- canonical 문서만 읽어도 프로젝트 목적을 이해할 수 있다
- reading 문서와 canonical 문서의 경계가 분명하다

현재 상태:

- 완료

### Phase 1. Tiny Analytic Evaluator Skeleton

목표:

- 문서 계약을 코드 타입과 함수 시그니처로 옮긴다
- toy case 기반 state / trajectory evaluator를 만든다
- base field와 exception layer를 separate output으로 유지한다
- CLI와 최소 테스트를 추가한다

완료 기준:

- semantic slot contract가 코드 타입으로 존재한다
- toy YAML case를 로드할 수 있다
- `evaluate-state`, `evaluate-trajectory`, `inspect-case`가 동작한다
- base / soft / hard가 한 scalar로 섞이지 않는다
- 최소 pytest가 통과한다

현재 상태:

- 완료

### Phase 2. Channel 실험과 Toy Case 확장

목표:

- progression, interior-boundary, continuity-branch 채널을 더 다양한 장면에서 시험한다
- toy case를 늘려 channel 의미를 더 분명하게 만든다
- ordering key와 hard/soft/base 분리가 충분히 직관적인지 검토한다

완료 기준:

- toy case 세트가 straight/bend/split 외의 중요한 local 장면을 포함한다
- 채널별 expected behavior가 문서와 테스트에 같이 반영된다
- ordering key의 prototype 기본형이 유지 가능한 수준인지 판단할 수 있다

현재 상태:

- 완료

### Phase 3. Local Raster Visualization

목표:

- 함수형 evaluator를 local query window에서 샘플링하여 시각화한다
- base / soft / hard를 채널별로 확인할 수 있는 debug view를 만든다

완료 기준:

- toy case에 대해 local field를 안정적으로 시각화할 수 있다
- 각 channel과 exception layer를 분리해서 볼 수 있다

현재 상태:

- 완료

### Phase 4. Parameter Lab

목표:

- 같은 semantic snapshot 위에서 field 파라미터를 바꾸며 비교 실험하는 연구용 툴을 만든다
- baseline/candidate와 preset 기반 비교 절차를 도구 수준에서 고정한다
- canonical 문서와 구현 사이의 드리프트를 줄인다

대표 작업:

- config-driven evaluator 경로 유지
- case 선택 + 파라미터 패널
- single / compare / diff view
- preset 저장 / 불러오기
- Apply 기반 parameter commit + background recompute
- canonical 문서와 구현 현황의 경계 정리

완료 기준:

- 코드 수정 없이 핵심 파라미터 비교가 같은 case 위에서 가능하다
- baseline/candidate 비교가 같은 effective context 위에서 반복 가능하다
- export bundle만으로 실험 재현에 필요한 preset snapshot과 session metadata가 남는다
- canonical 문서는 단일 progression field 기준으로 정리된다
- 구현의 config / preset / GUI naming도 단일 canonical progression field 기준으로 정렬된다
- canonical score sign이 `higher is better`로 문서와 구현에 같이 유지된다

현재 상태:

- 완료

late Phase 4 acceptance:

- acceptance 판단은 semantic-first로 유지한다
- overlap 영역 ordering stability가 유지된다
- visible endpoint가 semantic start/end처럼 보이지 않는다
- `straight_corridor`, `left_bend`, `split_branch`, `merge_like_patch`, `u_turn`에서 hole / abrupt ranking flip / fake end-cap이 없다
- cached runtime query layer와 evaluator semantics가 일치한다
- Parameter Lab export만으로 morphology 비교가 재현 가능하다
- 3D preview는 optional / post-Phase 4 polish로만 남긴다

판단:

- 위 acceptance를 현재 문서 / 구현 / 테스트 기준으로 충족한 상태로 본다

### Phase 5. Source Adapter

목표:

- canonical semantic contract를 실제 source에 연결하는 adapter를 만든다
- source-specific 자료구조를 canonical input slot으로 번역한다

완료 기준:

- 최소 한 종류의 외부 source를 canonical input으로 변환할 수 있다
- source-specific 구조가 canonical 내부로 새어 들어오지 않는다

현재 상태:

- 보류

현재 참고:

- Phase 5 방향의 현재 proposal은 canonical design이 아니라 reading 문서로만 남긴다
- proposal: `docs/reading/phase5_adapter_proposal_ko.md`

### Phase 6. Interactive Studio

목표:

- local raster visualization과 문서 모델을 결합한 실시간 편집형 studio를 만든다
- geometry / progression / layer를 수정하면서 field 변화를 즉시 볼 수 있게 한다

완료 기준:

- toy case를 실시간으로 수정하고 field를 다시 볼 수 있다
- base / soft / hard layer를 분리해서 inspection할 수 있다

현재 상태:

- 장기 과제

## 현재 체크리스트

### 완료

- canonical docs 정리
- reading / canonical 경계 분리
- conda env 준비
- tiny evaluator skeleton 구현
- sensor-only patch 중심 toy case 확장
- local raster visualization 추가
- pytest 기반 최소 검증 통과
- Parameter Lab 초기 compare workflow 구현
- canonical progression field 문서 재정의

### 현재 진행

- Phase 4 결과를 SSOT 상태로 유지
- downstream consumer가 사용할 runtime contract drift 방지
- morphology lab 기준선 유지

### 다음 액션

1. 이 repo에서는 Phase 4 결과를 안정 상태로 유지하고 drift만 관리
2. morphology 미세조정은 downstream 실험 결과가 생길 때만 되돌아와 수행
3. Phase 5 Source Adapter는 후속 단계로 유지

## 사용 원칙

- phase는 구현체가 아니라 프로젝트 truth 기준으로 갱신한다
- roadmap 본문은 현재 계획만 직접 설명한다
- 자세한 설계 근거는 `docs/design/`
- 구체 source 사례는 `docs/reading/`
- 내부 우선순위는 `docs/internal/priorities.md`
