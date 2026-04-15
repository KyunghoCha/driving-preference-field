# Input Reconstruction Notes

> 참고용 reading note다. canonical 정의는 `docs/reference/input_semantics_ko.md`와 `docs/reference/source_adapter_ko.md`를 기준으로 읽는다.

input/source 쪽에서 확인한 사실, 아직 고정하지 않은 질문, 그리고 SSC를 source example로만 읽을 때 필요한 대응 정보를 묶어 둔다. 이 문서를 읽는 이유는 두 가지다. 첫째, canonical contract가 실제 입력 품질과 어떻게 만나는지 보기 위해서다. 둘째, 아직 설계 SSOT로 승격하지 않은 관찰과 질문을 모아 두기 위해서다.

## 1. Semantic Support Conditions

### 현재 canonical 문서에서 이미 고정된 사실

- canonical input은 raw source가 아니라 semantic contract다
- canonical 입력의 최소 축은 `drivable semantics`와 `progression semantics`다
- canonical은 특정 geometry primitive를 필수 형식으로 강제하지 않는다
- canonical은 fixed source type이나 source-specific naming을 요구하지 않는다
- `ego_pose`는 snapshot 본체가 아니라 `QueryContext`에 속한다
- `local_window` 크기와 slicing policy는 canonical truth가 아니라 experiment 영역이다
- `support/confidence` transport shape와 exact weighting semantics는 experiment 영역이다
- branch winner는 canonical field가 직접 정하지 않는다

### 현재 대화에서 확인된 정보

- global path는 모든 적용 환경에서 항상 주어진다고 가정할 수 없다
- transverse 또는 longitudinal support scope를 global로 고정하는 것은 current canonical truth가 아니다
- support scope는 source가 제공할 수 있는 progression support 형태에 따라 달라질 수 있다
- discrete source input 자체는 금지 조건이 아니다
- discrete nodes, edges, paths, polygons 같은 입력도 semantic support로 번역되면 사용할 수 있다
- source가 충분한 semantic quality로 `drivable support`와 `progression support`를 복원하지 못할 수 있다
- 이 경우 runtime이 소비할 수 있는 semantic input은 partial 또는 weak support가 된다

### 아직 fixed truth로 올리지 않은 항목

- transverse support를 global-conditioned, local-conditioned, hybrid 중 어느 범위로 둘지
- longitudinal support를 global-conditioned, local-conditioned, hybrid 중 어느 범위로 둘지
- support scope selection policy를 canonical contract로 고정할지 여부
- semantic support quality가 약할 때 field를 어떤 degrade mode로 소비할지

## 2. Input Capability Tiers

이 절은 source가 어느 정도 semantic support를 복원할 수 있는지 대략적인 층위를 나눠 보는 메모다. canonical 정의가 아니라, 입력 품질을 비교할 때 쓰는 working view다.

### Tier 1. Sensor-Only Local Input

- 상대적으로 잘 채우는 slot:
  - drivable support
  - boundary / interior support
  - exception-layer support
- 상대적으로 약한 slot:
  - progression support
  - branch / continuity support

### Tier 2. Map-Assisted Input

- 잘 채우는 slot:
  - drivable support
  - progression support
  - boundary / interior support
- 보강되는 slot:
  - branch / continuity support

### Tier 3. Rich Structured Input

- 잘 채우는 slot:
  - drivable support
  - progression support
  - boundary / interior support
  - branch / continuity support
  - exception-layer support

## 3. SSC Mapping Example

이 절은 SSC를 canonical truth로 승격하지 않고 source example로만 남긴다. 실제 downstream source를 canonical slot에 어떻게 대응시킬 수 있는지 감을 잡기 위한 예시다.

| SSC raw source | 대응 가능한 canonical slot | 현재 수준 |
| --- | --- | --- |
| waypoint / ordered path / goal sequence | progression support | 바로 활용 가능 |
| graph / route continuity 정보 | progression support, branch / continuity support | adapter 필요 |
| local costmap obstacle / inflation | exception-layer support, 일부 boundary support | 바로 활용 가능 |
| lane layer / lane pointcloud | drivable support, boundary / interior support | adapter 필요 |
| local free-space shape | drivable support, boundary / interior support | adapter 필요 |

SSC는 prototype input source로는 유용하지만, canonical 입력 구조를 그대로 대체하지는 않는다.
