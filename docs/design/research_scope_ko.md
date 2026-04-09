# 연구 범위 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 `driving-preference-field`가 현재 정확히 무엇을 하려는지, 그리고 무엇을 아직 하려는 것이 아닌지를 고정한다.

이 문서의 목적은 세 가지다.

- 설계 대화와 구현 사이의 범위 드리프트를 줄인다
- 논문에서 주장 가능한 범위를 과장 없이 정리한다
- base field, path, 주행 가능 공간, 예외 레이어의 역할을 혼동하지 않게 한다

## 현재 연구 질문

현재 질문은 다음과 같다.

외부에서 주어지는 주행 가능 의미와 진행 의미를 바탕으로, 이상적인 주행 선호를 생성하는 base driving preference field를 정의할 수 있는가?

조금 더 풀어 쓰면:

- 주행 가능 의미가 이미 주어졌다고 할 때
- 공간 전체의 선호 구조를 생성하고
- 장애물이나 규칙 같은 예외는 별도 레이어로 다루며
- optimizer가 그 위에서 자연스럽게 좋은 trajectory를 만들게 할 수 있는가

## 이 연구가 하려는 것

### 1. 주행 의미를 공간 선호도로 표현하는 방식

핵심 관심사는 "어떤 경로점을 따라가야 하는가"보다 "공간 내 어떤 상태와 어떤 trajectory가 더 바람직한가"를 어떻게 표현할 것인가에 있다.

따라서 연구의 중심은:

- base driving preference field의 정의
- 그 field가 가져야 하는 성질
- 예외 레이어와의 분리 원칙
- optimizer와의 결합 가능성

이다.

### 2. 외부 semantics를 받아 field를 생성하는 구조

현재 연구는 주행 가능 공간을 직접 추출하는 문제를 다루지 않는다.

대신 다음이 외부에서 주어진다고 가정한다.

- 주행 가능 의미를 담는 drivable semantics
- 진행 의미를 부여할 수 있는 continuity / branch / direction semantics
- 이 둘을 현재 query context에 맞게 해석할 수 있는 semantic contract

그리고 연구의 관심은 이 입력을 받아 **base driving preference field를 생성하는 방식**에 있다.

### 3. base field와 예외 레이어의 분리

이 연구는 obstacle costmap 같은 repulsive layer와, ideal driving preference를 담는 base field를 같은 것으로 보지 않는다.

즉 최소한 다음은 분리되어야 한다.

- base driving preference field
- safety / obstacle layer
- rule / dynamic exception layer

### 4. 전역 의미와 지역 계산의 분리

이 연구에서 field는 개념적으로는 공간 전체에 대해 정의될 수 있다.

하지만 runtime 계산은 반드시 전역 dense raster일 필요가 없다.

즉:

- 의미론적으로는 global field
- runtime에서는 local analytic evaluation
- visualization에서는 optional full-field rendering

이라는 분리가 가능하다고 본다.

## 이 연구가 지금 하려는 것이 아닌 것

### 1. path generation 자체

이 연구는 ego에서 goal까지의 discrete path를 먼저 만드는 시스템 자체를 직접 제안하는 것이 아니다.

경로는 optimizer나 외부 semantics의 결과로 나타날 수 있지만, 현재 연구의 본체는 path planner가 아니라 field representation이다.

### 2. 주행 가능 공간 추출

이 연구는 perception이나 HD map processing으로 drivable area를 직접 추출하는 문제를 다루지 않는다.

### 3. 완성된 planner / controller 제안

이 연구는 아직 다음을 직접 완성하려는 단계가 아니다.

- full MPPI implementation
- complete planner stack
- vehicle dynamics-aware real-time control loop
- full external stack end-to-end deployment

### 4. obstacle layer와의 단순 가산 결합

이 연구는 base field와 obstacle layer를 단순 합으로만 해석하는 것을 목표로 하지 않는다.

## 논문에서 주장 가능한 범위

### 주장 가능한 것

- 주행 가능 의미와 진행 의미를 반영한 base field 표현의 필요성
- obstacle / rule / dynamic semantics와의 레이어 분리 필요성
- 샘플링 기반 최적화와 결합 가능한 표현 계층이라는 관점

### 아직 과장하면 안 되는 것

- 이 field만으로 planner 전체가 해결된다는 주장
- 실제 차량 성능 향상을 이미 증명했다는 주장
- lane change, split / merge, dynamic obstacle interaction을 모두 해결했다는 주장
- route generation 없이 전 문제를 해결할 수 있다는 주장

## 현재 기준 결론

한 줄로 요약하면 현재 연구는 다음을 목표로 한다.

외부에서 주어지는 주행 가능 의미와 진행 의미를 받아, 이상적인 주행 선호를 생성하는 base driving preference field를 정의하고, 예외 요소를 별도 레이어로 분리한 채 optimizer가 그 구조를 활용하게 만드는 표현 계층을 정리하는 것.
