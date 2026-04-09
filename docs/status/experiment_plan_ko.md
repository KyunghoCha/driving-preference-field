# 연구용 실험 계획 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 base driving preference field의 함수형과 파라미터를 연구용으로 비교하기 위한 실험 계획을 정리한다.

현재 비교 실험은 코드 수정으로 한 번씩 돌리는 작업이 아니라, Parameter Lab 위에서 preset과 export를 통해 반복 수행하는 절차를 기준으로 한다.

이 문서는 다음을 고정한다.

- 어떤 morphology 축을 비교할 것인가
- 어떤 파라미터를 변화시킬 것인가
- 어떤 toy case에서 차이를 볼 것인가
- 무엇을 baseline으로 둘 것인가
- 어떤 출력과 기록으로 결과를 남길 것인가

## 현재 실험 대상

우선순위는 progression-aware potential structure다.

이 구조는 다음 질문에 답할 수 있어야 한다.

- longitudinal term이 얼마나 강하게 progression gain을 만들 때 원하는 흐름을 유도하는가
- longitudinal frame을 `local absolute s`와 `ego-relative Δs` 중 어떻게 읽을 때 원하는 ordering이 나오는가
- transverse term이 얼마나 빠르게 감쇠할 때 원하는 cross-section shape가 나오는가
- longitudinal과 transverse를 독립적으로 조절했을 때 어떤 morphology가 나오는가
- support / confidence / continuity modulation이 weak-support 장면과 branch 장면에서 어떤 차이를 만드는가

## Parameter Lab 기준 비교 절차

각 실험은 다음 순서로 수행한다.

1. case를 고정한다
2. baseline preset을 선택한다
3. candidate preset을 선택한다
4. single / compare / diff view를 확인한다
5. render set과 parameter snapshot을 함께 남긴다
6. 짧은 정성 메모를 기록한다
7. `comparison_session.json`을 함께 남긴다
8. 필요하면 session-level ego/window control도 함께 기록한다
9. 필요하면 line cut / profile inspection 결과도 함께 남긴다

## 실험축

### 1. Longitudinal family

- 선형 ramp
- 완만하게 시작해 포화되는 family
- power 계열
- inverse-like family

### 2. Longitudinal amplitude / slope

- progression gain의 전체 세기
- slope / horizon / lookahead
- 미래 gain이 얼마나 빨리 커지는지

### 3. Longitudinal frame

- `local absolute s`
- `ego-relative Δs`
- 같은 파라미터라도 frame choice가 morphology와 ordering을 어떻게 바꾸는가

### 4. Transverse family

- inverse-distance 계열
- power-law 계열
- exponential-like 계열

### 5. Transverse spread / decay

- 축에서 벗어날수록 점수가 얼마나 빨리 줄어드는가
- 횡방향 penalty의 폭과 decay가 morphology를 어떻게 바꾸는가

### 6. Support / confidence / continuity modulation

- weak-support 장면에서 과확신이 줄어드는가
- branch / merge / reconnect 장면에서 continuity 차이가 유지되는가
- alignment 같은 보조 gate가 reverse나 명백한 비양립 상태만 약하게 누르는가

## baseline과 candidate의 역할

baseline과 candidate는 특정 버전 이름이 아니라 **역할**로만 정의한다.

- baseline:
  - 현재 비교 기준
  - 더 단순하거나 약한 longitudinal/transverse 조합
  - progression term이 없는 control case도 포함 가능
- candidate:
  - 비교하려는 새 family 또는 새 parameter set
  - longitudinal / transverse / support modulation 중 하나 이상이 달라진 조합

reference preset은 존재할 수 있지만, preset 파일명이나 과거 구현 이름은 canonical 실험축이 아니다.

## 공통 실험 케이스

Phase 3까지 만든 toy case를 기본 실험 집합으로 둔다.

- `straight_corridor`
- `left_bend`
- `u_turn`
- `split_branch`
- `sensor_patch_open`
- `sensor_patch_narrow`
- `sensor_patch_blocked`
- `merge_like_patch`

## 출력과 기록 방식

각 실험 조합마다 다음을 남긴다.

- baseline render set
- candidate render set
- diff view
- parameter snapshot
- `comparison_session.json`
- profile inspection bundle
  - `profile_baseline.png`
  - `profile_candidate.png`
  - `profile_diff.png`
  - `profile_data.json`
- 채널별 PNG
  - `progression_tilted`
  - `interior_boundary`
  - `continuity_branch`
  - `base_total`
  - `safety_soft`
- hard mask PNG
- `composite_debug.png`
- `render_legend.png`
- `render_summary.json`
- 짧은 비교 메모
  - 어떤 morphology 변화가 보였는가
  - 자연 contour인지, 구현 artifact인지
  - weak-support 장면에서 과확신이 생겼는가
  - branch/merge 장면에서 continuity가 사라지지 않았는가

## 정성 평가 기준

다음 질문에 대해 yes/no 또는 짧은 메모를 남긴다.

- straight에서 longitudinal gain이 progression axis를 따라 분명히 보이는가
- frame choice를 바꿨을 때 가까운 중심과 더 먼 좋은 영역 사이 ordering이 의미 있게 달라지는가
- bend에서 field가 단순 직선 gradient가 아니라 휘어진 patch처럼 읽히는가
- split에서 branch continuity가 구분되는가
- merge-like 장면에서 continuity ambiguity를 풀어주는가
- open patch에서 progression이 과도하게 확신하지 않는가
- blocked patch에서 safety layer가 base를 완전히 덮어쓰지 않으면서도 hard/soft 구분이 유지되는가
- longitudinal과 transverse를 각각 바꿨을 때 morphology 변화가 분리되어 보이는가
- line cut/profile inspection에서 `s_hat`, `n_hat`, longitudinal/transverse component가 contour 원인을 설명하는가
- visible endpoint 근처에서 fake end-cap이나 ranking flip이 생기지 않는가

## late Phase 4 semantic acceptance

현재 late Phase 4 실험에서는 자연 contour와 인공 artifact를 구분해서 기록한다.

허용:

- bend/U-turn에서 보이는 대각선 contour
- 2D heatmap에서 비틀린 면처럼 보이는 global 등고선

제거 대상:

- overlap 영역 ordering flip
- visible endpoint saturation wall 또는 fake end-cap
- branch 사이 hole
- active-set / neighborhood artifact가 만든 abrupt jump

실험 결과는 숫자 threshold보다 아래 semantic 기준을 우선 기록한다.

- ordering 보존
- continuity 유지
- local peak 부재
- export bundle만으로 같은 morphology 비교 재현 가능

## 현재 단계 결론

이 문서의 목적은 아직 최적 수식을 확정하는 것이 아니다.

현재 단계의 목적은 다음과 같다.

- longitudinal / transverse 독립 실험축을 고정한다
- 같은 case와 같은 출력 형식으로 비교 가능한 절차를 유지한다
- 이후 코드 cleanup과 canonical model 정렬 뒤에도 반복 실험이 가능하게 만든다
