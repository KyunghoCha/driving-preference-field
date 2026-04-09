# Runtime Evaluation Contract 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 base field의 의미와 runtime 계산 방식을 분리해서 고정하고, analytic prototype이 따를 최소 evaluator contract를 정리한다.

이 문서에서 canonical score는 **higher is better**로 읽는다.

## 핵심 구분

### 1. 의미론

base field는 개념적으로 progression-aware potential field다.

즉:

- 현재 local map 전체에서 어디가 더 바람직한가
- progression axis를 따라 점수가 어떻게 변하는가
- progression axis에서 벗어날수록 점수가 어떻게 변하는가

를 말할 수 있어야 한다.

이 field는 최소한 다음 성분을 가진다.

- longitudinal / progression term
- transverse term
- support / confidence / continuity gate 같은 secondary modulation

canonical은 exact 결합식을 고정하지 않는다.

- runtime 구현은 하나의 current formula를 가질 수 있다
- 하지만 문서 SSOT는 longitudinal / transverse / secondary gate의 역할만 고정한다

### 2. runtime 계산

runtime에서는 항상 전역 dense map을 만들 필요가 없다.

가능한 기본형은 다음이다.

- ego-centric local frame
- local query window 전체를 대상으로 하는 analytic evaluator
- candidate state 또는 rollout state sequence 평가

즉 canonical representation은 **local map 전체를 평가하는 함수형 evaluator**일 수 있다.

또한 같은 semantic snapshot과 같은 effective local context에 대해 evaluator 설정만 바꿔 다시 평가할 수 있어야 한다.

즉 evaluator는 config-driven 구조를 지원해야 한다.

특히 progression field는 current local map 전체를 대상으로 longitudinal term과 transverse term을 조합한 patch를 평가할 수 있어야 하며, heading alignment는 필요하더라도 주성분이 아니라 secondary gate로만 남겨둘 수 있다.

current implementation은 다음을 사용한다.

- longitudinal frame:
  - `local_absolute`
  - `ego_relative`
- progression 본체:
  - smooth skeleton anchor들의 Gaussian elliptical blend로 local map 전체의 whole-fabric continuous function을 만든다
  - branch 사이도 별도 winner 없이 같은 함수 안에서 메운다
- exact formula:
  - `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`
- 따라서 runtime은 center-high transverse profile과 stronger longitudinal tilt가 동시에 만드는 ordering을 평가해야 한다.

### 3. visualization

full-field raster는:

- 디버깅
- 설명
- 논문 그림
- 파라미터 직관 확인

을 위한 secondary representation으로 본다.

prototype 단계에서는 local query window 전체를 격자로 샘플링한 PNG export나 GUI raster view가 기본 시각화 형태가 될 수 있다.

즉 raster는 field 본체가 아니라, local map 위에서 연속 함수를 샘플링한 secondary visualization이다.

시각화 스케일은 evaluator 의미를 가리지 않는 방향으로 고정한다.

- 일반 채널 heatmap은 채널별 고정 range와 unit을 가진다
- 기본 모드는 0을 절대 최소값으로 두는 fixed scale이다
- diff는 0 중심 대칭 range를 사용한다
- normalized view가 필요하면 그것은 별도 exploratory mode로만 둔다
- 어떤 mode를 쓰더라도 현재 range와 unit은 함께 표시한다

## 최소 Evaluator Contract

### 1. Query Context

runtime evaluator는 최소한 다음 context를 받는다.

- canonical semantic contract snapshot
- evaluator config
- ego-centric local frame
- local query window
- optional mode / phase context

### 2. State Evaluation

state evaluator는 다음 개념 출력을 제공해야 한다.

- `base_preference_channels`
- `soft_exception_channels`
- `hard_violation_flags`
- optional diagnostic metadata

즉 state 평가는 단일 scalar만 반환하는 것을 canonical로 두지 않고, layer-wise result를 먼저 반환하는 구조를 기본으로 둔다.

개별 channel score와 trajectory-level base score는 모두 `higher is better`로 읽는다. diff는 `candidate - baseline`이다.

config를 바꾼 비교 실험도 이 contract 위에서 가능해야 한다.

### 3. Trajectory Evaluation

trajectory evaluator는 state evaluation의 누적으로 해석한다.

- 입력:
  - query context
  - rollout state sequence
- 출력:
  - `trajectory_base_preference_channels`
  - `trajectory_soft_exception_channels`
  - `trajectory_hard_violation_flags`
  - optional derived ordering key

trajectory hard violation은 horizon 전체에서 하나라도 발생하면 유지된다.

trajectory soft / base channel은 누적 또는 집계되며, 구체 가중 방식은 prototype에서 정한다.

trajectory 비교도 single evaluation과 같은 evaluator contract를 공유해야 하며, 같은 semantic snapshot + 같은 effective local context + 같은 config/preset pair로 반복 가능한 비교가 가능해야 한다.

## optimizer와의 관계

이 문서는 optimizer를 구현하지 않는다.

하지만 다음은 고정한다.

- optimizer는 field generator의 소비자다
- field는 optimizer보다 먼저 정의돼야 한다
- trajectory는 field를 읽는 결과로 나타나야 한다

예를 들어 MPPI 같은 샘플링 기반 optimizer는 이 contract를 소비하는 구현 중 하나일 수 있다. 하지만 canonical은 특정 optimizer에 종속되지 않는다.

## 현재 기준 결론

한 줄로 요약하면:

field는 의미론적으로 progression-aware potential field이고, runtime에서는 current local map 전체를 analytic하게 평가할 수 있으며, visualization은 optional rendering이고, evaluator는 layer-wise state/trajectory result를 반환하는 함수형 contract로 본다.
