# Base Field 기초 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 새 프로젝트의 최상위 개념 SSOT다.

이 문서의 핵심은 `base driving preference field`다. 즉 주행 가능한 의미와 진행 의미가 주어졌을 때, **현재 보이는 local map 전체**에 대해 어떤 상태와 어떤 trajectory가 더 바람직한지를 생성하는 preference structure를 먼저 정의한다.

## 출발점

이 문서의 출발점은 다음 문제의식이다.

- 특정한 한 줄의 reference만으로는 이상적인 주행 흐름을 충분히 표현하기 어렵다
- 지금 당장 가장 직접적인 선택이 항상 좋은 주행선을 만들지는 않는다
- 이상적인 trajectory는 더 먼 progression gain 때문에 현재 약간 돌아가는 선택을 포함할 수 있다
- base field는 단일 discrete path가 아니라 공간 전체의 선호 구조를 만들어야 한다
- obstacle, rule, dynamic actor 같은 예외는 base field 본체와 분리해야 한다

## base driving preference field란 무엇인가

이 문서에서 base field는 다음을 뜻한다.

- source-agnostic semantic input을 받아 생성되는 preference generator
- 현재 query context의 local map 전체에 대해 정의되는 potential-like structure
- 어떤 상태와 trajectory가 더 바람직한지를 생성하는 선호 구조
- planner나 optimizer가 자연스럽게 trajectory를 만들 수 있게 하는 기반 표현

즉 base field는 입력 semantics 자체가 아니라, 입력 semantics를 바탕으로 생성되는 **공간 전체의 선호 분포**다.

## 중요한 성질

이 field는 최소한 다음 성질을 가져야 한다.

### 0. score sign은 higher is better다

canonical score는 **높을수록 더 선호되는 값**으로 둔다.

- 3D surface를 뒤집어 그리거나, 우물처럼 보이게 표현하는 것은 visualization 선택일 뿐이다
- canonical 의미와 evaluator ordering은 `higher is better`를 기준으로 읽는다

### 1. 진행축과 횡방향 구조를 함께 가진다

전방이라는 말보다 정확한 표현은 **진행축 방향 성분과 횡방향 성분을 함께 가진다**는 것이다.

즉:

- progression axis를 따라 점수가 어떻게 기울어지는지 정의해야 한다
- progression axis에서 벗어날수록 점수가 어떻게 변하는지도 정의해야 한다
- longitudinal term과 transverse term은 서로 독립적으로 함수 family와 파라미터를 가질 수 있다
- longitudinal 좌표를 어떤 frame으로 읽을지도 실험 대상이 될 수 있다
  - local support 위 absolute progress
  - ego 기준 상대 progress
- progression axis는 field의 주축이지, 항상 pointwise 최고점일 필요는 없다

### 2. local map 전체에 potential surface를 만든다

field는 일부 좁은 띠 안에서만 작동하는 local pattern에 머물면 안 된다.

개념적으로는 현재 보이는 local map 전체의 각 점을

- progression / longitudinal 좌표
- transverse 좌표

로 읽고, 그 위에 하나의 preference surface를 생성하는 쪽으로 본다.

즉 canonical 중심은 “reference 근처 점수 계산”이 아니라 **local map 전체를 덮는 progression-aware potential surface**다.

같은 progression slice에서는 중심이 가장 높게 보일 수 있지만, longitudinal tilt가 충분히 강하면 더 먼 progression gain이 가까운 중심 선호를 이길 수 있다. 즉 이상적인 trajectory는 바로 앞 중심을 반드시 통과하지 않아도 된다.

현재 보이는 local map 전체에서:

- 어디가 progression gain을 더 많이 가지는가
- 어디가 횡방향으로 더 자연스러운가
- 어디가 더 좋은 continuation으로 이어지는가
- 어디가 더 안정적인 support를 가지는가

같은 차이를 만들어야 한다.

### 3. support와 gate는 보조 성분이다

이 field는 progression 축과 횡방향 profile이 주성분이고, 다음은 보조적으로 field를 조절하는 성분으로 둔다.

- support / confidence
- branch / continuity
- heading alignment

즉 support와 gate는 field의 존재를 보조적으로 조절할 수 있지만, field를 단순한 nearest-reference scoring으로 축소해서는 안 된다.

canonical은 exact 결합식을 고정하지 않는다.

- 어떤 current implementation은 longitudinal tilt와 transverse profile을 더할 수 있다
- 다른 current implementation은 다른 형태의 coupling을 쓸 수 있다

하지만 support / confidence / continuity / alignment는 어디까지나 **secondary modulation**으로만 취급한다.

## current implementation note

canonical은 exact 결합식을 고정하지 않지만, 현재 구현은 다음 형태를 사용한다.

- current implementation은 nearest winner가 아니라 **smooth skeleton anchor들을 좌표 control point로 보고 Gaussian elliptical blend로 만든 whole-fabric continuous function**을 사용한다
- branch 사이도 guide별 patch를 따로 만들지 않고, 같은 함수 안에서 fabric-like surface로 메운다
- `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`
- `transverse_component`는 같은 진행 slice에서 center-high profile을 만든다
- `longitudinal_component`는 더 먼 progression gain을 더한다
- `higher is better`를 유지하며, strong longitudinal 설정에서는 farther-ahead off-center point가 nearer-center point보다 높아질 수 있다

### 4. base field는 ideal preference를 담는다

이 field는 일차적으로 ideal driving preference를 담는 층이다.

즉 obstacle, dynamic actor, rule violation 같은 현실의 예외를 본체에 섞어 넣는 것이 아니라, 먼저 이상적 선호 구조를 정의하는 쪽이 우선이다.

### 5. 의미론은 global, 계산은 local일 수 있다

field의 의미가 global하다고 해서 runtime 계산도 항상 전역 dense map일 필요는 없다.

가능한 해석은 다음과 같다.

- 의미론은 global progression continuity와 양립해야 한다
- 실제 계산은 current query의 local map 전체에서 analytic하게 수행할 수 있다
- full raster rendering은 visualization/debugging용 secondary representation이다

즉 canonical은 giant map object보다 **local map 전체를 평가하는 함수형 field generator**에 더 가깝다.

## canonical이 아닌 것

다음은 base field의 중심 개념이 아니다.

- 특정 source 이름
- 특정 geometry primitive
- 특정 GUI 구현
- 특정 버전 비교 서술

예시 source나 과거 구현 비교는 reading 자료나 status 메모로만 다룬다.

## 현재 기준 결론

한 줄로 요약하면:

이 프로젝트의 핵심은 source-agnostic progression semantics를 받아, 현재 보이는 local map 전체에 대해 **longitudinal term + transverse term + secondary support/gate**를 가진 base driving preference field를 정의하고, optimizer가 그 위에서 자연스러운 trajectory를 만들게 하는 표현을 정리하는 것이다.
