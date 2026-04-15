# 입력 Semantics

이 문서는 base driving preference field가 어떤 입력 계약을 전제로 하는지 정리한다. 여기서 고정하는 것은 특정 센서나 지도 형식이 아니라, field generator가 소비하는 semantic slot이다.

## 정의

- canonical 입력은 raw source가 아니라 semantic contract다.
- source-specific naming, geometry primitive, fixed source type은 canonical이 아니다.
- base field의 최소 입력 축은 `drivable semantics`와 `progression semantics`다.
- exception layer용 의미는 base field 입력과 같은 층으로 취급하지 않는다.

## 필수 semantic slot

### 1. Drivable Support

현재 문맥에서 어떤 상태가 주행 가능한 구조 안에 있는지를 뒷받침한다.

- 최소 의미:
  - local query space에서 어떤 영역 또는 상태가 물리적으로 이어질 수 있는지 구분 가능해야 한다.
- 선택 의미:
  - drivable confidence
  - local width
  - occupancy-free support
- field generator 해석:
  - base field가 정의될 수 있는 지지 공간을 제공한다.

drivable support는 움직일 수 있는 공간을 알려주지만, progression ordering 자체를 대신하지는 않는다.

### 2. Progression Support

현재 intended progression과 양립하는 방향과 상태 변화를 뒷받침한다.

- 최소 의미:
  - local query context에서 progression axis를 유도할 수 있어야 한다.
  - local map 전체에서 longitudinal / transverse 선호 구조를 만들 progression hint가 있어야 한다.
- 선택 의미:
  - reverse context
  - future anchor
  - phase or mode context
  - optional support confidence
- field generator 해석:
  - progression-aware potential structure를 만든다.

progression support는 discrete winner direction을 직접 고르는 입력이 아니라, local map 전체의 before / after ordering을 만드는 progression hint다.

## Optional semantic slot

### 3. Boundary / Interior Support

- 최소 의미:
  - 현재 상태가 interior 쪽인지 boundary 쪽인지 구분 가능해야 한다.
- 선택 의미:
  - left / right boundary relation
  - local margin estimate
  - local width tendency
- field generator 해석:
  - interior preference와 boundary relation을 생성한다.

### 4. Branch / Continuity Support

- 최소 의미:
  - 대안적 continuation 사이의 continuity relation을 구분할 수 있어야 한다.
- 선택 의미:
  - optional branch priority
  - merge preference
  - optional continuity confidence
- field generator 해석:
  - continuity / branch structure를 생성한다.

### 5. Exception-Layer Support

- 최소 의미:
  - obstacle / safety semantics
  - rule-related semantics
  - dynamic interaction semantics
- field generator 해석:
  - base field 생성에는 직접 쓰지 않고 composition 단계에서 separate layer로 처리한다.

## 부분 입력

실제 source는 progression support나 drivable support를 완전하게 채우지 못할 수 있다. sparse progression hint, weak continuity cue, partial drivable boundary 같은 입력은 canonical contract의 일부를 약하게 채우는 것으로 해석한다. 현재 adapter 경로에서는 optional branch/support/confidence가 없다고 canonical output 전체를 invalid로 보지 않는다.

## 비범위

다음은 canonical input의 필수 형식이 아니다.

- 특정 geometry primitive
- 특정 reference 표현 형식
- fixed source type
- 선호도 label 자체
- source adapter의 raw source naming
- `ego_pose`를 snapshot 본체에 넣는 특정 규칙
- local window 크기나 slicing policy의 고정값

`ego_pose`, local window policy, support/confidence transport shape 같은 항목은 semantic slot 본체보다 `QueryContext` 또는 experiment 영역에 가깝다. source adapter output contract는 [source_adapter_ko.md](./source_adapter_ko.md)에서 고정한다.

## 현재 기준

base driving preference field의 canonical 입력은 `drivable semantics + progression semantics`를 중심으로 한 semantic contract이며, source-specific 형식은 reading 사례로만 다룬다.
