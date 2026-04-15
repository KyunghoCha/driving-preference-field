# 실험 계획

이 문서는 base driving preference field의 함수형과 파라미터를 비교하기 위한 현재 실험 절차를 정리한다. 비교 실험은 코드 수정으로 한 번씩 돌리는 작업이 아니라, Parameter Lab 위에서 preset과 export를 통해 반복 수행하는 절차를 기준으로 한다.

## 현재 phase

- 현재 실험은 `Phase 5 완료, Phase 6 준비 상태`를 전제로 한다.
- hand-authored toy case와 generic adapter fixture를 같은 canonical snapshot contract로 비교할 수 있다.

## 현재 실험 대상

우선순위는 progression-aware potential structure다. 현재 실험은 다음 질문에 답하려고 한다.

- longitudinal term이 progression gain을 얼마나 강하게 만들 때 원하는 흐름을 유도하는가
- longitudinal frame을 `local absolute s`와 `ego-relative Δs` 중 어떻게 읽을 때 원하는 ordering이 나오는가
- transverse term이 얼마나 빠르게 감쇠할 때 원하는 cross-section shape가 나오는가
- longitudinal과 transverse를 독립적으로 조절했을 때 어떤 morphology가 나오는가
- support / confidence / continuity modulation이 weak-support 장면과 branch 장면에서 어떤 차이를 만드는가

## 비교 절차

1. case를 고정한다.
2. baseline preset을 선택한다.
3. candidate preset을 선택한다.
4. `Single`, `Compare`, `Diff`를 확인한다.
5. 필요하면 `Profile` 탭과 profile inspection export를 함께 본다.
6. render set, parameter snapshot, qualitative note를 남긴다.
7. `comparison_session.json`을 함께 남긴다.
8. 필요하면 session-level ego/window control도 같이 기록한다.

## 실험축

### Longitudinal

- family
- amplitude / slope
- horizon / lookahead
- `local absolute s`
- `ego-relative Δs`

### Transverse

- family
- spread / decay
- penalty strength

### Support / confidence / continuity

- weak-support 장면에서 과확신이 줄어드는가
- branch / merge / reconnect 장면에서 continuity 차이가 유지되는가
- alignment 같은 보조 gate가 reverse나 명백한 비양립 상태만 약하게 누르는가

## baseline과 candidate

baseline과 candidate는 특정 버전 이름이 아니라 비교 역할이다.

- baseline:
  - 현재 비교 기준
  - 더 단순하거나 약한 longitudinal/transverse 조합
  - progression term이 없는 control case도 포함 가능
- candidate:
  - 비교하려는 새 family 또는 새 parameter set
  - longitudinal / transverse / support modulation 중 하나 이상이 달라진 조합

## 공통 케이스

기본 실험 집합:

- `straight_corridor`
- `left_bend`
- `u_turn`
- `split_branch`
- `sensor_patch_open`
- `sensor_patch_narrow`
- `sensor_patch_blocked`
- `merge_like_patch`

generic adapter fixture:

- `fixtures/adapter/straight_corridor_generic.yaml`
- `fixtures/adapter/left_bend_generic.yaml`
- `fixtures/adapter/split_branch_generic.yaml`

## 출력

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

## late Phase 4 semantic acceptance

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

## 현재 focus

- longitudinal / transverse 독립 실험축을 유지한다.
- 같은 case 또는 generic adapter fixture와 같은 출력 형식으로 비교 가능한 절차를 유지한다.
- 이후 코드 cleanup과 canonical model 정렬 뒤에도 반복 실험이 가능하게 만든다.

## 비범위

- 최적 수식의 최종 확정
- downstream integration 자체
- optimizer-specific tuning을 이 문서 기준으로 고정하는 일
