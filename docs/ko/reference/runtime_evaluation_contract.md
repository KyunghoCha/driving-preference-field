# 런타임 계약

이 문서는 base field의 의미와 runtime 계산 방식을 분리해서 정리하고, 현재 repo가 제공하는 public runtime interface와 evaluator contract를 고정한다. canonical score는 `higher is better`로 읽는다. 여기서 고정하는 것은 public runtime contract와 layer split이며, current tiny evaluator의 구체 합성 규칙은 별도 `현재 구현` 문단에서만 다룬다.

## 정의

- field는 의미론적으로 `whole-space preference field`이며, 진행 인지 포텐셜 장(`progression-aware potential field`)으로 읽는다.
- runtime에서는 항상 전역 dense map을 만들 필요가 없다.
- raster는 local map 위에서 연속 함수를 샘플링한 secondary visualization이다.
- downstream consumer는 current formula를 복제하지 않고 runtime layer를 소비한다.
- soft / hard burden은 base field와 별도 계층이다.

## 이 field가 말하는 것

field는 현재 local map 전체에서 어디가 더 바람직한지, progression axis를 따라 점수가 어떻게 변하는지, progression axis에서 벗어날수록 점수가 어떻게 변하는지를 말할 수 있어야 한다.

이 field는 최소한 다음 성분을 가진다.

- longitudinal / progression term
- transverse term
- support / confidence / continuity gate 같은 secondary modulation

canonical은 exact 결합식을 고정하지 않는다. 문서 SSOT는 longitudinal / transverse / secondary gate의 역할만 고정하고, exact current formula는 별도 현재 구현 reference에서 관리한다.

## 공개 런타임 인터페이스

Phase 5 current public runtime interface는 다음과 같다.

- `build_field_runtime(snapshot, context, config=None)`
- `FieldRuntime.query_state(state)`
- `FieldRuntime.query_trajectory(trajectory)`
- `FieldRuntime.query_debug_grid(x_coords, y_coords)`
- `FieldRuntime.query_progression_points(x_values, y_values, heading_yaws=None)`
- `FieldRuntime.query_progression_trajectories(trajectories_xy, heading_yaws=None)`

toy loader output과 generic source adapter output은 모두 같은 canonical contract로 이 runtime interface에 들어온다.

## 런타임 평가

runtime evaluator는 local map 전체를 analytic하게 평가할 수 있어야 한다.

- 입력:
  - canonical semantic contract snapshot
  - evaluator config
  - `QueryContext`
- 기본형:
  - ego-centric local frame
  - local query window 전체를 대상으로 하는 analytic evaluator
  - candidate state 또는 rollout state sequence 평가

## 보장해야 하는 성질

- cache 사용 여부가 semantic drift를 만들지 않는다.
- evaluator entrypoint와 `FieldRuntime` layer가 의미상 같은 progression-centered base 결과를 반환한다.
- overlap 영역 ordering stability와 endpoint continuation acceptance를 runtime layer가 깨지 않는다.
- batched progression query 결과는 같은 snapshot/context/config에서 `query_state` / `query_trajectory` ordering과 모순되지 않는다.
- generic source adapter output도 toy case와 같은 runtime interface로 직접 소비할 수 있다.

## 계층별 evaluator 계약

state evaluator는 다음 개념 출력을 제공해야 한다.

- `base_preference_channels`
- optional diagnostic metadata

trajectory evaluator는 state evaluation의 누적으로 해석한다.

- 입력:
  - query context
  - rollout state sequence
- 출력:
  - `trajectory_base_preference_channels`
  - optional derived ordering key

costmap / exception burden은 raster와 rendering 경로에서만 남긴다. public runtime payload는 progression-centered base field와 그 debug coordinate를 보여주는 쪽으로 제한한다.

## 현재 구현

현재 구현은 progression guide마다 Gaussian anchor blend로 guide-local progress coordinate를 계산하고, 각 guide의 transverse term은 그 guide 중심 구조까지의 최단거리로 읽은 뒤, guide-local score를 만들고 guide 간 hard max envelope를 취한다. score와 대부분의 debug coordinate는 dominant guide 기준 값을 유지하지만, `transverse_component`는 near-tied guide candidate의 transverse term을 부드럽게 섞은 inspection channel이다.

현재 tiny evaluator는 `base_preference_total = progression_tilted`로 읽는다. trajectory ordering도 progression total만 기준으로 한 prototype을 사용한다. `safety_soft`, `rule_soft`, `dynamic_soft`, hard mask는 visualization / costmap 성격의 burden channel로만 남고 public runtime payload에는 싣지 않는다.

## 시각화

full-field raster는 다음을 위한 보조 표현이다.

- 디버깅
- 설명
- 논문 그림
- 파라미터 직관 확인

일반 채널 heatmap은 채널별 고정 range와 unit을 가지고, 기본 모드는 0을 절대 최소값으로 두는 fixed scale이다. diff는 0 중심 대칭 range를 사용한다. normalized view가 필요하면 exploratory mode로만 둔다.

## 이 contract와 optimizer의 관계

이 문서는 optimizer를 구현하지 않는다. 다만 다음은 고정한다.

- optimizer는 field generator의 소비자다.
- field는 optimizer보다 먼저 정의돼야 한다.
- trajectory는 field를 읽는 결과로 나타나야 한다.

MPPI 같은 샘플링 기반 optimizer는 이 contract를 소비하는 구현 중 하나일 수 있지만, canonical은 특정 optimizer에 종속되지 않는다.

## 현재 기준

field는 progression-aware potential field이고, runtime에서는 current local map 전체를 analytic하게 평가할 수 있으며, evaluator는 layer-wise state/trajectory result를 반환하는 함수형 contract로 본다.
