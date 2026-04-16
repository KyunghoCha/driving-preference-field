# Input Reconstruction Notes

> 참고용 reading note다. canonical 정의는 `docs/ko/reference/input_semantics.md`와 `docs/ko/reference/source_adapter.md`를 기준으로 읽는다.

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

## 4. Deferred Scenario Questions

다음 장면은 아직 canonical input이나 toy-case 기본 집합으로 올리지 않고 연구 보류로 둔다. 이유는 장면 자체가 어려워서가 아니라, progression guide를 split / merge / circulation 구조에서 어떻게 표현할지 먼저 더 정리해야 하기 때문이다.

- 교차로:
  - 복수 continuation이 동시에 보이는 교차 영역에서 progression guide를 어떤 단위로 나눌지 아직 고정하지 않았다.
- 회전교차로:
  - entry / circulation / exit ordering을 어떤 progression guide 집합으로 표현할지 아직 더 검토가 필요하다.
- 중앙선, 고어 영역, 보행 영역 같은 rule-heavy geometry:
  - multi-lane corridor보다 richer rule semantics가 먼저 들어오므로, rule layer와 progression guide의 책임 분리가 더 정리된 뒤에 다루는 편이 낫다.

반대로 단순 multi-lane corridor는 현재 toy-case 집합에 추가할 수 있다. 이 경우 핵심은 “차선 여러 개가 있는 직선/곡선 공간에서 progression guide를 여러 개 둘 수 있는가”를 보는 것이지, 교차로 의미를 한 번에 해결하는 것이 아니다.

## 5. Current Surface Quality Notes

현재 `progression_surface.py`는 Gaussian anchor blend로 guide-local coordinate를 만들고 hard max envelope를 사용한다. exported transverse만 handoff 근처에서 스무딩한다. projection-based coordinate 실험은 롤백했고, 현재 품질 조정은 blended coordinate 위에서 split/merge handoff morphology를 다듬는 쪽으로 남아 있다.

현재 남은 질문은 coordinate drift 자체보다 morphology tuning 쪽에 가깝다.

- `two_lane_straight`:
  - lane center 두 개와 그 사이 valley는 현재 구현에서도 나온다.
- `left_bend`:
  - center ridge 안정성은 좋아졌지만, 곡률이 큰 구간에서 transverse profile이 얼마나 더 일정해야 하는지는 여전히 quality tuning 항목이다.
- `split_branch` / `merge_like_patch`:
  - hard max envelope와 guide handoff가 만드는 morphology가 현재 semantics와는 일관되지만, split/merge 내부와 바깥쪽 경계를 얼마나 더 자연스럽게 만들지는 추가 검토가 필요하다.

즉 다음 품질 배치에서 볼 핵심은 “guide-local coordinate를 다시 바꿀 것인가”보다, “현재 blended coordinate 위에서 split/merge handoff morphology를 어디까지 더 다듬을 것인가”다.
