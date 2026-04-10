# Parameter Lab 설계 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 연구용 Parameter Lab의 목적, 범위, 기본 동작, 출력 형태와 현재 구현 상태를 고정한다.

Parameter Lab은 geometry를 편집하는 studio가 아니라, 같은 semantic snapshot과 같은 effective local context 위에서 field 파라미터를 바꾸며 비교 실험하는 도구다. 또한 이 툴은 optimizer나 integration runtime을 붙이는 도구가 아니라, **morphology 해석과 current implementation 비교를 위한 연구용 랩**으로 본다.

## 툴 목적

Parameter Lab의 목적은 다음과 같다.

- 코드 수정 없이 field 파라미터를 바꿔 바로 재평가한다
- baseline과 candidate를 같은 case 위에서 비교한다
- qualitative note를 붙여 한 번의 비교를 실험 세션으로 남긴다
- single view, compare view, diff view를 통해 채널 구조 변화를 확인한다
- preset을 저장하고 다시 불러와 반복 가능한 비교 실험을 만든다

## Tool Semantics

Parameter Lab이 다루려는 canonical 파라미터 축은 다음과 같다.

### 1. Longitudinal / Progression 축

- progression axis를 따라 점수가 얼마나 기울어지는가
- 어떤 frame으로 longitudinal 좌표를 읽는가
  - `local absolute s`
  - `ego-relative Δs`
- 어떤 함수 family를 쓰는가
- amplitude / slope / lookahead를 어떻게 두는가
- local map 전체에서 진행방향 morphology가 어떻게 변하는가

### 2. Transverse 축

- progression axis에서 벗어날수록 점수가 어떻게 변하는가
- 어떤 횡방향 family를 쓰는가
- spread / decay / penalty strength를 어떻게 두는가
- 경로 중심 횡단면 profile이 얼마나 넓고 날카로운가

### 3. Support / Gate 축

- support confidence를 얼마나 강하게 반영하는가
- branch / continuity를 어떤 강도로 gate처럼 걸 것인가
- alignment 같은 보조 항을 얼마나 약하게 남길 것인가
- score sign은 `higher is better`로 읽고, diff는 `candidate - baseline`으로 읽는다

즉 Parameter Lab의 본체는 특정 source 예시를 만지는 것이 아니라, **longitudinal + transverse + support/gate** 축을 바꾸며 local map 전체의 field morphology를 비교하는 것이다.

## 1차 범위

현재 초기 구현에서 Parameter Lab은 다음을 포함한다.

- case 선택
- generic adapter input path 직접 열기
- case-level ego/window control
- baseline / candidate parameter 패널
- single view
- compare view
- diff view
- preset 저장
- preset 불러오기
- baseline/candidate 복사
- summary metrics 표시
- qualitative note 입력
- comparison export

이 단계에서는 geometry를 수정하지 않는다.

## 비범위

다음은 현재 Parameter Lab 범위에 포함하지 않는다.

- geometry 편집
- progression guide 편집
- region draw/edit
- source adapter
- Gazebo / RViz / MPPI integration
- studio canvas
- interactive drawing

## preset과 세션

preset은 evaluator 설정의 저장 단위다.

preset은 최소한 다음을 포함한다.

- preset name
- `FieldConfig`
- optional note
- optional metadata

Parameter Lab은 baseline/candidate를 같은 case와 같은 effective context 위에서 비교하고, export를 통해 실험 세션을 남긴다.

session export에는 최소한 다음이 남아야 한다.

- case path
- selected channel
- effective ego pose
- effective local window
- baseline/candidate preset snapshot
- profile summary
- qualitative note
- summary metrics

## Apply 기반 파라미터 반영

Parameter Lab에서 파라미터 편집은 기본적으로 `staged edit -> Apply`로 처리한다.

- slider
- spinbox
- dropdown

같은 파라미터 변경은 panel 안에서 먼저 누적되고, `Apply`를 눌렀을 때 evaluator를 다시 호출하도록 본다.

반면 아래처럼 명시적인 액션은 바로 재계산해도 된다.

- case 변경
- case control apply/reset
- preset load
- baseline/candidate copy

## 시각화 스케일

Parameter Lab은 현재 선택된 채널에 대해 표시 스케일을 함께 보여준다.

- 기본 mode: `Fixed`
- optional mode: `Normalized`

`Fixed`는 채널별 고정 range를 사용한다.

- 일반 채널은 `0`을 절대 최소값으로 둔다
- diff는 `0` 중심 대칭 range를 사용한다
- 같은 채널이면 baseline과 candidate가 같은 색-값 대응을 공유한다

`Normalized`는 현재 화면 값 범위를 다시 매핑하는 exploratory mode다.

- baseline/candidate/diff는 각자의 현재 값 범위에 맞춰 다시 매핑될 수 있다
- 따라서 이 mode는 구조 탐색용이며, 고정 해석용 기준은 아니다

## Current Implementation Note

현재 repo에는 PyQt6 기반 Parameter Lab 초기 구현이 존재한다.

- CLI: `python -m driving_preference_field parameter-lab`
- baseline/candidate compare, single, diff view 지원
- toy case와 generic adapter input 둘 다 같은 canonical snapshot contract로 열 수 있다
- case-level ego/window control 지원
- preset 저장 / 불러오기 / 복사 / export 지원
- fixed / normalized scale mode 지원
- parameter help와 summary 지원
- 기본 selected channel은 `progression_tilted`다
- profile inspection 탭으로 line cut / profile plot을 같이 볼 수 있다

다만 현재 구현은 canonical 전체를 다 노출하지는 않는다.

- GUI는 progression frame/longitudinal/transverse/support ceiling 축을 직접 노출한다
- 현재 panel은 `Longitudinal`, `Transverse`, `Support / Gate` 그룹으로 나뉜다
- interior_boundary, continuity_branch, exception layer 파라미터는 아직 직접 노출하지 않는다
- 즉 현재 GUI는 canonical 전체를 모두 편집하는 studio가 아니라, progression field compare tool에 집중돼 있다
- current implementation은 하나의 local-map-wide progression score를 계산하며, 현재 exact formula는 다음과 같다
  - nearest winner가 아니라 smooth skeleton anchor를 좌표 control point로 쓰는 Gaussian-blended whole-fabric continuous function이다
  - branch 사이도 빈공간 없이 fabric-like surface로 이어진다
  - visible guide endpoint는 virtual continuation으로 처리되어 semantic start/end처럼 읽히지 않는다
  - `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`
  - transverse는 같은 진행 slice에서 center-high profile을 만든다
  - longitudinal은 더 먼 progression gain을 더한다
  - support / alignment는 shape를 만드는 주성분이 아니라 약한 secondary modulation이다
  - strong longitudinal 설정에서는 바로 앞 중심을 꼭 통과하지 않아도 더 좋은 ordering이 나올 수 있다
  - GUI/PNG raster는 이 함수를 local map 위에서 샘플링한 결과다
  - debug view로 `s_hat`, `n_hat`, `longitudinal_component`, `transverse_component`, `support_mod`, `alignment_mod`를 같이 볼 수 있다
  - profile inspection export는 baseline/candidate/diff profile PNG와 `profile_data.json`을 남긴다
  - 3D preview는 현재 범위가 아니며, 2D profile inspection을 morphology 해석의 우선 도구로 둔다

즉 문서는 canonical 의미를 먼저 설명하고, 현재 GUI는 그 의미의 일부만 구현한 상태로 기록한다. Parameter Lab은 현재도 downstream integration tool이 아니라 **whole-space field morphology를 읽고 비교하는 해석 도구**로 유지한다.

## 현재 기준 결론

Parameter Lab은 다음을 우선으로 하는 연구용 도구다.

- case 고정
- session-level context control
- Apply 기반 파라미터 반영
- baseline/candidate 비교
- preset 기반 반복 실험
- 비교 세션 export

canonical 의미는 **source-agnostic progression field의 longitudinal / transverse / support-gate 축**이고, 현재 GUI 구현은 그중 progression frame / longitudinal / transverse / support ceiling 축을 다루는 compare tool이다.
