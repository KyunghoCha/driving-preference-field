# Phase 5 Adapter Proposal History

- 역할: reading
- 현재성: non-canonical
- 대상 독자: maintainer
- 다음으로 읽을 문서: [05. Source Adapter](../../reference/source_adapter_ko.md)

> 이 문서는 canonical truth가 아니다.
> 현재 상태: reading / history / proposal
> canonical 관련 문서: `docs/reference/source_adapter_ko.md`

작성일: 2026-04-10

## 문서 목적

이 문서는 현재 대화에서 나온 Phase 5 adapter 방향을 **proposal / reading** 수준으로만 기록한다.

이 문서는 canonical design SSOT가 아니다. 아직 구현 전이며, source adapter 방향을 이후에 다시 검토하기 위한 working proposal이다.

현재 canonical 결정은 아래 design SSOT에 반영됐다.

- `docs/reference/source_adapter_ko.md`

이 문서는 이제 **proposal history / reading 기록**으로만 유지한다.

## 현재 proposal 핵심

### 1. adapter는 의미 번역기만 한다

adapter의 역할은 raw source를 canonical 의미로 번역하는 것이다.

즉:

- raw source -> canonical semantic contract

까지만 담당하고, planner heuristic, winner selection, 행동 결정은 하지 않는다.

### 2. progression과 drivable을 분리해서 본다

현재 proposal은 canonical 입력을 다음 두 축으로 보는 쪽에 가깝다.

- progression support
- drivable support

drivable은 현재 움직일 수 있는 공간을, progression은 앞/뒤 ordering과 intended progression continuity를 제공한다.

이 proposal에서는 local drivable region이 progression support를 조금 벗어나도 **주행 의미 자체는 남아 있어야 한다**는 생각을 중요하게 본다.

### 3. ego pose는 snapshot 본체보다 query context에 가깝다

현재 proposal에서는 `ego_pose`를 canonical snapshot 본체의 필수 semantic slot로 보지 않는다.

이유는:

- ego가 field 의미 자체를 재정의하면 canonical intent가 흔들릴 수 있기 때문이다

따라서 ego pose는 field 본체 의미보다:

- query 위치
- window placement
- optional `ego_relative` frame evaluation

같은 **runtime context** 쪽에 더 가깝다고 본다.

### 4. local window 정책은 실험 영역이다

현재 proposal은 local window 크기와 slicing policy를 canonical truth로 고정하지 않는다.

이유는:

- 차량/속도/상황에 따라 달라질 수 있고
- 너무 크면 next-next intent가 과하게 보일 수 있고
- 너무 작으면 progression 의미가 잘리지 않을지 다시 봐야 하기 때문이다

즉 local window policy는 현재 proposal 기준으로 **experiment 영역**이다.

### 5. branch winner는 canonical에서 정하지 않는다

현재 proposal은 branch가 있어도 canonical field가 winner branch를 강제로 정하지 않는 쪽을 선호한다.

가능한 방향은:

- canonical은 공간 ordering만 제공
- branch winner나 최종 방향 결정은 행동계획/optimizer가 담당

다만 global planner나 route planner에서 branch prior가 있다면, 그것을 **soft prior**로 field에 반영할 가능성은 열어둘 수 있다.

### 6. support/confidence는 optional weak prior로 남길 수 있다

support/confidence는 본체 의미가 아니라 quality prior로 본다.

가능한 역할:

- weak-support 장면에서 과확신을 줄임
- branch ambiguity 장면에서 품질이 낮은 support를 약하게만 낮춤

다만 이것도 현재 proposal 단계이며, exact semantics와 반영 강도는 실험 영역으로 남긴다.

### 7. SSC는 특수한 validation source다

SSC는 중요한 validation 환경이지만 canonical 기준이 아니다.

이 proposal은 다음을 전제로 한다.

- SSC는 downstream validation source다
- SSC에서 나온 요구사항은 evidence로 사용한다
- SSC 자료구조나 planner state를 그대로 canonical input에 올리지 않는다

## proposal에서 아직 미정인 것

아래는 아직 결정 완료가 아니다.

- `progression_supports`의 canonical 데이터 형태
- `drivable_regions`를 polygon 중심으로 둘지 더 일반화할지
- branch prior를 canonical slot로 둘지 여부
- support/confidence를 어떤 형태로 실어 나를지
- adapter validation fixture를 어떤 source 모양으로 시작할지

## 현재 위치

이 proposal은 **Phase 5 준비용 reading 문서**다.

즉:

- Phase 4 완료 상태를 바꾸지 않는다
- design canonical 문서를 수정하는 기준이 아니다
- 이후 Phase 5를 시작할 때 decision doc 초안의 입력으로 사용한다

## 현재 기준 결론

한 줄로 요약하면:

현재 Phase 5 proposal은 adapter를 “의미 번역기”로 두고, progression과 drivable을 분리해서 보며, ego/window/support 같은 항목은 canonical 본체가 아니라 runtime context 또는 실험 영역으로 두는 방향이다.
