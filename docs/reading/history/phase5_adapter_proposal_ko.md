# Phase 5 Adapter Proposal History

> 참고용 proposal history다. 현재 source adapter 결정은 `docs/reference/source_adapter_ko.md`를 기준으로 읽는다.

현재 대화에서 나왔던 Phase 5 adapter 방향을 proposal 수준으로 남겨 둔 기록이다. 구현 전 단계에서 어떤 판단이 논의됐는지 보존하는 것이 목적이며, design SSOT를 대신하지 않는다.

## 현재 proposal 핵심

### 1. adapter는 의미 번역기만 한다

adapter의 역할은 raw source를 canonical 의미로 번역하는 것이다.

- raw source -> canonical semantic contract

여기까지만 담당하고, planner heuristic, winner selection, 행동 결정은 하지 않는다.

### 2. progression과 drivable을 분리해서 본다

이 proposal은 canonical 입력을 두 축으로 보는 쪽에 가깝다.

- progression support
- drivable support

drivable은 현재 움직일 수 있는 공간을, progression은 앞/뒤 ordering과 intended progression continuity를 제공한다.

### 3. ego pose는 snapshot 본체보다 query context에 가깝다

`ego_pose`를 canonical snapshot 본체의 필수 semantic slot로 보기보다, query 위치, window placement, optional `ego_relative` frame evaluation 같은 runtime context 쪽에 더 가깝게 본다.

### 4. local window 정책은 실험 영역이다

local window 크기와 slicing policy를 canonical truth로 고정하지 않는다. 차량, 속도, 장면에 따라 달라질 수 있고, 너무 크면 다음 구간 의도가 과하게 보일 수 있으며, 너무 작으면 progression 의미가 잘릴 수 있기 때문이다.

### 5. branch winner는 canonical에서 정하지 않는다

branch가 있어도 canonical field가 winner branch를 강제로 정하지 않는다. 공간 ordering은 field가 제공하고, winner나 최종 방향 결정은 행동계획/optimizer가 담당한다.

### 6. support/confidence는 optional weak prior로 남길 수 있다

support/confidence는 본체 의미가 아니라 quality prior로 본다. weak-support 장면에서 과확신을 줄이고, branch ambiguity 장면에서 품질이 낮은 support를 약하게만 낮추는 용도를 염두에 두지만, exact semantics와 반영 강도는 실험 영역으로 남긴다.

### 7. SSC는 특수한 validation source다

SSC는 중요한 validation 환경이지만 canonical 기준이 아니다.

- SSC는 downstream validation source다
- SSC에서 나온 요구사항은 evidence로 사용한다
- SSC 자료구조나 planner state를 그대로 canonical input에 올리지 않는다

## proposal에서 아직 미정인 것

- `progression_supports`의 canonical 데이터 형태
- `drivable_regions`를 polygon 중심으로 둘지 더 일반화할지
- branch prior를 canonical slot로 둘지 여부
- support/confidence를 어떤 형태로 실어 나를지
- adapter validation fixture를 어떤 source 모양으로 시작할지

## 현재 위치

이 문서는 Phase 5를 준비하던 시점의 proposal history다. Phase 4 완료 상태를 바꾸지 않았고, 이후 design SSOT를 쓰기 위한 입력으로만 사용됐다.
