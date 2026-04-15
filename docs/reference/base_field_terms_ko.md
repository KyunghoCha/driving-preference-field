# Base Field 항

- 역할: reference
- 현재성: canonical
- 대상 독자: contributor
- 다음으로 읽을 문서: [Layer 조합](./layer_composition_ko.md)

작성일: 2026-04-08

## 문서 목적

이 문서는 base driving preference field가 어떤 종류의 선호 구조를 생성해야 하는지 정리한다.

이 문서는 아직 최종 수식을 고정하지 않는다. 대신 구현자가 evaluator를 설계할 수 있을 정도로 각 항의 역할, 입력 소비, 해석 단위를 먼저 고정한다.

## 필수 항

### 1. Progression-Aware Potential Structure

이 항은 현재 local map 전체에 대해 progression-aware surface patch를 생성한다.

- 입력 소비:
  - progression support
  - optional branch / continuity support
- spatial preference:
  - current local map의 각 점은 개념적으로 progression / longitudinal 좌표와 transverse 좌표를 함께 가진다
  - progression axis를 따라 점수가 어떻게 변하는지 결정한다
  - progression axis에서 벗어날수록 점수가 어떻게 변하는지도 함께 결정한다
  - longitudinal 좌표는 local support 위 absolute progress 또는 ego-relative progress 차이로 읽을 수 있다
  - progression axis는 field의 주축이지만, 항상 pointwise 최고점일 필요는 없다
  - 더 앞쪽의 progression gain이 횡방향 penalty보다 크면 축보다 앞쪽이나 옆쪽이 더 높게 나올 수 있다
  - global하게는 더 긴 progression continuity와 양립하는 surface를 상상하고, runtime에서는 current local map 위의 patch를 읽는다
- state 평가:
  - 현재 상태가 progression surface 안에서 어느 위치의 preference를 가지는지 읽는다
- trajectory 평가:
  - horizon 전체에서 progression-consistent한 흐름을 유지하는 trajectory를 높게 읽는다
- 아직 열어둘 부분:
  - longitudinal term과 transverse term을 어떤 결합식으로 합칠지
  - longitudinal term 함수 family
  - longitudinal amplitude / slope / horizon
  - transverse term 함수 family
  - transverse spread / decay / penalty strength
  - support / confidence modulation 강도
  - branch / continuity gate 반영 방식
  - heading alignment를 얼마나 보조적으로만 남길지

현재 구현은 가산형 surface를 쓴다.

- `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`
- 같은 longitudinal slice에서는 center-high transverse profile을 읽는다
- strong longitudinal 설정에서는 더 먼 progression gain이 가까운 중심 선호를 이길 수 있다
- smooth skeleton anchor는 점수 carrier가 아니라 local space coordinates를 부드럽게 추정하는 control point로 읽는다
- visible guide endpoint는 semantic endpoint가 아니라 local patch continuation이 있는 것으로 읽는다
- support / alignment modulation은 주형을 만들지 못하게 약한 secondary로만 남긴다

### 2. Interior / Boundary-Derived Preference

이 항은 주행 가능한 구조의 interior와 boundary 관계로부터 공간적 선호를 생성한다.

- 입력 소비:
  - drivable support
  - boundary / interior support
- spatial preference:
  - interior에 더 안정적으로 머무르는 상태와 boundary에 과도하게 붙는 상태를 구분한다
  - progression term과 별개로 local cross-section shape를 만든다
- state 평가:
  - 한 시점의 상태가 interior 쪽인지, boundary를 스치고 있는지 읽는다
- trajectory 평가:
  - 전체 trajectory가 interior에서 안정적으로 이어지는지 읽는다
- 아직 열어둘 부분:
  - medial tendency를 explicit하게 둘지
  - boundary-derived preference만으로 충분한지
  - margin 감쇠율

### 3. Continuity / Branch Structure

이 항은 여러 continuation 중 어떤 흐름이 더 자연스럽게 이어지는지를 생성한다.

- 입력 소비:
  - progression support
  - branch / continuity support
- spatial preference:
  - split, merge, reconnect, branch 장면에서 더 일관적인 흐름을 선호하게 만든다
  - progression field를 source-agnostic하게 유지하면서 continuation ambiguity를 푸는 보조 구조를 만든다
- state 평가:
  - 현재 상태가 어느 continuation과 더 잘 정합되는지 읽는다
- trajectory 평가:
  - trajectory 전체가 하나의 continuity structure를 일관되게 따르는지 읽는다
- 아직 열어둘 부분:
  - branch priority의 사용 방식
  - ambiguous branch 처리
  - continuity confidence 반영 강도

## 선택 / 실험 항

다음은 canonical 필수 항은 아니지만 이후 prototype에서 실험 가능한 항이다.

- heading affinity
- curvature sensitivity
- vehicle-state / dynamics bias
- comfort / smoothness coupling

이 항들은 base field를 보강할 수 있지만, 현재 단계의 최소 contract에는 포함하지 않는다.

## 항 사이의 관계

현재 canonical에서 항 사이의 역할 분담은 다음처럼 본다.

- progression-aware potential structure가 field의 longitudinal / transverse 주성분을 만든다
- interior / boundary-derived preference가 local cross-section shape를 보강한다
- continuity / branch structure가 대안적 이어짐 사이의 선호를 만든다

즉 세 항은 같은 의미를 반복하는 것이 아니라, 서로 다른 차원의 선호 구조를 담당한다.

## 현재 기준 결론

base field는 최소한:

- progression-aware potential structure
- interior / boundary-derived preference
- continuity / branch structure

를 생성할 수 있어야 하며, 추가 항은 이후 prototype에서 실험적으로 확장한다.
