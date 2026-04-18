# 분기/split baseline 승격 승인 discipline

## Date

- 2026-04-18

## Topic

- `branch/split baseline promotion approval discipline`

## Source sessions

- current active DPF thread; the user explicitly treated the current thread as the authoritative source for the workflow correction

## User original messages

> 지금 많이 더러워지지 않았어? 확인좀

> 그 우리가 분기 시작하고 나서 더러워진거잖아 너가 승인 안하고 baseline으로 올려서 그거 일단 명시해두고 skill에 그리고 더 생각해보자

> 커밋 메시지 잘 남겨뒀지? 몇번째 baseline인지도 기록해놔 그래야 보기 편하니까

> 해줘 skill에도

## Baseline sequence locked in this thread

- `B1 = 5efe84d`
  - `docs(raw): widen source anchors through 3/17+ sessions`
  - surface 실험 전 기준점
- `B2 = d609f76`
  - `surface: replace hard-max progression merge with pooled blend`
  - 승인 없이 올라간 pooled-blend 실험
- `B3 = 03eb593`
  - `surface: make transverse component purely pooled`
  - 승인 없이 올라간 purely-pooled transverse 실험
- `B4 = c779121`
  - `surface: localize transverse reading around pooled progress`
  - 승인 없이 올라간 local-window transverse 실험
- `B5 = eb3022a`
  - `surface: make transverse guide-faithful`
  - 승인 없이 올라간 guide-faithful transverse 실험
- `B6 = ded4f59`
  - `surface: smooth guide-faithful transverse reading`
  - 승인 없이 올라간 smoothed guide-faithful transverse 실험
- `B7 = 57ee191`
  - `Revert "surface: localize transverse reading around pooled progress"`
  - `B2`~`B6` 계열 실험을 걷어낸 복귀 baseline
- `B8 = 23436f1`
  - `surface: drop transverse handoff smoothing`
  - `b3a4efa` 시절 수식 계열로 다시 맞춘 baseline
- `B9 = 1d9d102`
  - `surface: restore transverse handoff smoothing`
  - 사용자 승인 후 승격된 baseline
- `B10 = 2d9b99f`
  - `surface: use guide-center distance for transverse term`
  - 현재 작업 기준 baseline

## Discipline added from this point

- branch/split morphology 조사 중 baseline 후보는 `B{n}` 번호와 commit hash를 함께 기록한다.
- 사용자 explicit approval 없이 `B{n+1}`을 `main` baseline으로 선언하거나 승격하지 않는다.
- docs-only/workflow commits는 baseline 번호에 넣지 않는다. baseline 번호는 behavior-changing surface baseline에만 쓴다.

## Open questions at the time

- branch/split morphology investigation에서 어떤 시점을 baseline 승격 후보로 부를 수 있는지
- explicit approval을 어떤 수준의 사용자 지시로 볼지
- historical comparison worktree를 언제 정리할지
