# Reference-Path Cost Model 구성 항목

이 문서는 base local reference path cost가 어떤 종류의 ordering 구조를 생성해야 하는지 항별로 정리한다. 최종 수식을 고정하기보다, evaluator를 설계할 수 있을 정도로 각 항의 역할과 입력 소비를 먼저 분리해 둔다.

## 필수 항

### 1. progression-aware potential structure

현재 local map 전체에 대해 progression-aware surface patch를 생성한다.

- 입력 소비:
  - progression support
  - optional branch / continuity support
- 만들어야 하는 구조:
  - progression axis를 따라 점수가 어떻게 변하는지
  - progression axis에서 벗어날수록 점수가 어떻게 변하는지
  - longitudinal 좌표를 absolute progress 또는 ego-relative progress 차이로 읽을 수 있는지
- trajectory 해석:
  - progression-consistent한 흐름을 높게 읽는다.

현재 구현은 `score = support_mod * alignment_mod * (transverse_term + longitudinal_gain * longitudinal_component)` 형태의 가산형 surface를 사용한다. 같은 longitudinal slice에서는 center-high transverse profile을 읽고, strong longitudinal 설정에서는 더 먼 progression gain이 가까운 중심 score를 이길 수 있다.

### 2. interior / boundary 기반 선호

주행 가능한 구조의 interior와 boundary 관계로부터 공간적 선호를 생성한다.

- 입력 소비:
  - drivable support
  - boundary / interior support
- 만들어야 하는 구조:
  - interior에 안정적으로 머무르는 상태와 boundary에 과도하게 붙는 상태를 구분한다.
  - progression term과 별개로 local cross-section shape를 보강한다.

### 3. continuity / branch 구조

여러 continuation 중 어떤 흐름이 더 자연스럽게 이어지는지를 생성한다.

- 입력 소비:
  - progression support
  - branch / continuity support
- 만들어야 하는 구조:
  - split, merge, reconnect, branch 장면에서 continuity relation을 읽는다.
  - continuation ambiguity를 풀어 주는 보조 구조를 만든다.

## 선택 실험 항목

다음은 canonical 필수 항은 아니지만 이후 prototype에서 실험 가능한 항이다.

- heading affinity
- curvature sensitivity
- vehicle-state / dynamics bias
- comfort / smoothness coupling

## 항 사이의 관계

- progression-aware potential structure가 longitudinal / transverse 주성분을 만든다.
- interior / boundary-derived ordering가 local cross-section shape를 보강한다.
- continuity / branch structure가 대안적 이어짐 사이의 선호를 만든다.

## 현재 기준

reference-path cost model는 최소한 progression-aware potential structure, interior / boundary-derived ordering, continuity / branch structure를 생성할 수 있어야 하며, 추가 항은 이후 prototype에서 확장한다.
