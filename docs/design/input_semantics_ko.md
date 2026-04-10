# 입력 Semantics 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 base driving preference field가 어떤 입력 계약을 전제로 하는지 고정한다.

이 문서에서 입력은 데이터 source가 아니라 **semantic contract**다. 즉 특정 센서, 특정 지도, 특정 reference geometry는 canonical이 아니며, field generator가 소비하는 의미 단위만 고정한다.

## 핵심 원칙

- 이 프로젝트는 raw perception을 직접 canonical 입력으로 두지 않는다
- 이 프로젝트는 특정 source 자료구조를 canonical 입력으로 두지 않는다
- 이 프로젝트는 **주행 가능 의미와 진행 의미**를 입력으로 받는다
- 선호는 입력이 직접 라벨링하는 것이 아니라 field generator가 생성한다
- exception layer용 의미는 base field 입력과 같은 층으로 취급하지 않는다

## Canonical Input Interface

현재 canonical input interface는 다음 semantic slot으로 구성된다.

이 문서에서 중요한 구분은 다음이다.

- canonical은 지금 **확정된 semantic slot**만 고정한다
- source adapter가 이것을 어떤 output contract로 번역하는지는 `docs/design/source_adapter_ko.md`에서 고정한다
- `ego_pose`, local window policy, support/confidence transport shape 같은 것은 semantic slot 본체보다 QueryContext 또는 experiment 영역에 더 가깝다

### 1. Drivable Support

이 slot은 어떤 상태가 현재 문맥에서 주행 가능한 구조 안에 있는지를 뒷받침한다.

- 최소 의미:
  - local query space에서 어떤 영역 또는 상태가 물리적으로 이어질 수 있는지 구분 가능해야 한다
- 선택 의미:
  - drivable confidence
  - local width
  - occupancy-free support
- field generator 해석:
  - base field가 정의될 수 있는 지지 공간을 제공한다

drivable support는 움직일 수 있는 공간을 알려주지만, progression ordering 자체를 대신하지는 않는다.

### 2. Progression Support

이 slot은 어떤 방향과 상태 변화가 현재 intended progression과 양립하는지를 뒷받침한다.

- 최소 의미:
  - local query context에서 progression axis를 유도할 수 있어야 한다
  - current local map 전체에서 longitudinal / transverse 선호 구조를 만들 수 있는 progression hint가 있어야 한다
- 선택 의미:
  - reverse context
  - future anchor
  - phase or mode context
  - optional support confidence
- field generator 해석:
  - progression-aware potential structure를 만든다

progression support는 “무엇이 앞이고 뒤인가”를 정해주는 ordering support다. 이것은 discrete winner direction을 직접 고르는 action input이 아니라, local map 전체에서 longitudinal / transverse structure를 만들게 하는 progression hint다.

### 3. Boundary / Interior Support

이 slot은 주행 가능한 구조 안에서 interior와 boundary의 관계를 뒷받침한다.

- 최소 의미:
  - 현재 상태가 interior 쪽인지 boundary 쪽인지 구분 가능해야 한다
- 선택 의미:
  - left / right boundary relation
  - local margin estimate
  - local width tendency
- field generator 해석:
  - interior preference와 boundary relation을 생성한다

### 4. Branch / Continuity Support

이 slot은 split, merge, branch, reconnect 같은 장면에서 어떤 이어짐이 더 자연스러운지를 뒷받침한다.

- 최소 의미:
  - 대안적 continuation 사이의 continuity relation을 구분할 수 있어야 한다
- 선택 의미:
  - optional branch priority
  - merge preference
  - optional continuity confidence
- field generator 해석:
  - continuity / branch structure를 생성한다

### 5. Exception-Layer Support

이 slot은 base field를 만들기 위한 입력이 아니라, safety / rule / dynamic layer를 위한 separate semantics다.

- 최소 의미:
  - obstacle / safety semantics
  - rule-related semantics
  - dynamic interaction semantics
- field generator 해석:
  - base field 생성에는 직접 쓰지 않고, composition 단계에서 separate layer로 처리한다

## 부분 입력은 어떻게 취급하는가

실제 source는 progression support나 drivable support를 완전하게 채우지 못할 수 있다.

예를 들어 어떤 source는 다음만 부분적으로 줄 수 있다.

- sparse progression hint
- weak continuity cue
- partial drivable boundary

이 경우 해당 source는 canonical contract의 일부만 약하게 채우는 것으로 해석한다. 즉 부분 입력은 canonical contract의 **약한 instantiation**일 수는 있지만, canonical contract 자체를 대체하지 않는다.

Phase 5 current adapter는 이런 부분 입력을 generic source adapter output으로 번역할 수 있게 하되, optional branch/support/confidence가 없다고 canonical output 전체를 invalid로 보지는 않는다.

## Canonical이 요구하지 않는 것

다음은 canonical input의 필수 형식이 아니다.

- 특정 geometry primitive
- 특정 reference 표현 형식
- fixed source type
- 선호도 label 자체
- source adapter의 raw source naming
- ego pose를 snapshot 본체에 넣는 특정 규칙
- local window 크기나 slicing policy의 고정값

즉 canonical은 “무슨 파일/센서에서 왔는가”보다 “어떤 semantic slot을 어느 정도 채울 수 있는가”를 기준으로 본다.

## 현재 기준 결론

한 줄로 요약하면:

base driving preference field의 canonical 입력은 `drivable semantics + progression semantics`를 중심으로 한 semantic contract이며, source-specific 형태는 reading 사례로만 다룬다.
