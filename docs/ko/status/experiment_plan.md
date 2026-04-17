# 실험 계획

이 문서는 DPF 비교 실험을 어떻게 실행하고 기록할지 정리한다. morphology를 대충 보는 페이지가 아니라, 실험을 비교 가능하고 설명 가능하고 되돌릴 수 있게 유지하는 실행 문서다.

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

## baseline은 무엇을 뜻하나

DPF 실험에서는 baseline이 하나만 있는 것이 아니다.

- `code baseline`: 실험이 출발하는 clean commit, branch, worktree
- `comparison baseline`: candidate를 직접 비교하는 preset/config/case 묶음
- `historical baseline`: 새 방향이 실제로 나아졌는지 보기 위해 다시 가져오는 이전 상태
- `rollback baseline`: 실험이 틀렸을 때 되돌아갈 clean state

실제로는 `commit + case + local context + preset`이 같이 있어야 DPF baseline이 된다. commit만 같아도 case나 local window, preset이 다르면 같은 baseline으로 보기 어렵다.

## 권장 실험 격리 방식

`main`은 clean reference baseline으로 둔다. 실험은 한 branch당 한 가지 의미 있는 가설만 두고, 다른 작업과 섞일 가능성이 크면 worktree를 따로 두는 편이 맞다.

refactor와 behavior change도 한 배치에 섞지 않는 편이 좋다. 둘 다 필요하면 분리해서, 무엇을 바꿨고 무엇을 고정했는지 설명할 수 있게 만든다.

## 비교 절차

1. 실험이 case나 local context를 바꾸는 것이 아니라면, 그 둘을 먼저 고정한다.
2. comparison baseline preset과 candidate preset을 고른다.
3. 먼저 `progression_tilted`에서 baseline과 candidate를 비교한다.
4. `Diff`를 확인한다.
5. spatial view만으로 설명이 부족하면 `Profile`을 확인한다.
6. 남길 가치가 있는 차이라면 comparison bundle을 export한다.

## 실험축

### 종방향

- family
- amplitude / slope
- horizon / lookahead
- `local absolute s`
- `ego-relative Δs`

### 횡방향

- family
- spread / decay
- penalty strength

### support / confidence / continuity

- weak-support 장면에서 과확신이 줄어드는가
- branch / merge / reconnect 장면에서 continuity 차이가 유지되는가
- alignment 같은 보조 gate가 reverse나 명백한 비양립 상태만 약하게 누르는가

## 실험을 어떻게 기록하나

commit subject는 무엇이 바뀌었는지를 말하는 편이 좋다. commit body는 왜 바꾸는지, 무엇을 개선하려는지, 무엇은 바꾸지 않으려는지를 적는 편이 맞다.

실험 문맥을 오래 남겨야 한다면 commit body나 trailer에 구조화된 정보를 같이 남긴다. 예를 들면:

- `Baseline`: 기준 code baseline 또는 reference commit
- `Compare-Against`: 직접 비교한 baseline experiment나 historical state
- `Verification`: 테스트, case, export, 수동 확인 경계

목표는 rigid template를 강제하는 것이 아니다. 나중에 다시 봤을 때 가설, baseline, verification 경계를 복원할 수 있게 만드는 것이다.

## verify, discard, recombine

코드를 바꾸기 전에 무엇이 좋아져야 하고 무엇이 깨지면 안 되는지부터 정하는 편이 좋다. 보통은 acceptance case, regression surface, non-goal을 먼저 적어 두는 것이 맞다.

실험이 한 target은 개선했지만 다른 중요한 surface를 망쳤다면, 같은 dirty state 위에 patch를 계속 덧칠하지 않는 편이 좋다. 실패한 방향은 discard하고 clean baseline으로 돌아간 뒤 다시 시작한다. 두 방향이 모두 가치가 있으면, clean baseline에서 의도적으로 recombine한다.

## 리뷰가 잡아야 할 것

리뷰는 immediate correctness만 보면 부족하다. 이 repo에서는 특히 다음도 같이 봐야 한다.

- dead code
- dead formula path
- unused knob
- 실패한 실험에서 남은 stale implementation residue
- docs/code mismatch
- unnecessary complexity 또는 over-engineering

목표는 완벽함이 아니라, accepted change가 repo를 더 읽기 쉽고 더 비교하기 쉽고 더 진화시키기 쉽게 남기는 것이다.

## 공통 케이스

기본 실험 집합:

- `straight_corridor`
- `two_lane_straight`
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
  - `safety_soft`
  - `rule_soft`
  - `dynamic_soft`
- hard mask PNG
- `composite_debug.png`
- `render_legend.png`
- `render_summary.json`
- 짧은 비교 메모

export bundle는 원래 편집 세션이 끝난 뒤에도 같은 차이를 설명할 수 있어야 한다.

## 현재 focus

- longitudinal / transverse 독립 실험축을 유지한다.
- 같은 case 또는 generic adapter fixture와 같은 출력 형식으로 비교 가능한 절차를 유지한다.
- progression field는 본체 채널로, safety / rule / dynamic은 costmap 성격 시각화로 분리한 뒤에도 반복 실험이 가능하게 만든다.

## 비범위

- 최적 수식의 최종 확정
- downstream integration 자체
- optimizer-specific tuning을 이 문서 기준으로 고정하는 일
- 영구적인 Git workflow 하나를 canonical truth로 박아 두는 일

## 보류 중인 장면

- 교차로:
  - progression guide를 어떤 단위로 나눌지 더 검토가 필요하다.
- 회전교차로:
  - circulation ordering과 entry/exit 표현을 아직 고정하지 않았다.
