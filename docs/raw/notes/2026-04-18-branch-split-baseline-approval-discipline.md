# 분기/split baseline 승격 승인 discipline

## Date

- 2026-04-18

## Topic

- `branch/split baseline promotion approval discipline`

## Source sessions

- current active LRPC thread; the user explicitly treated the current thread as the authoritative source for the workflow correction

## User original messages

> 지금 많이 더러워지지 않았어? 확인좀

> 그 우리가 분기 시작하고 나서 더러워진거잖아 너가 승인 안하고 baseline으로 올려서 그거 일단 명시해두고 skill에 그리고 더 생각해보자

> 커밋 메시지 잘 남겨뒀지? 몇번째 baseline인지도 기록해놔 그래야 보기 편하니까

> 해줘 skill에도

> raw 는 이제 실시간으로 중요한거 같으면 업데이트를 해줘 baseline으로 된거만 모아서 중간중간 실험하고 실패한거는 언급만 하고 지금까지 한거도 추가를 하고 그렇게 skill이나 다른데도 기록해두고

## Baseline sequence locked in this thread

- `B1 = 5efe84d`
- `B1 = 5efe84d`
  - `2026-04-18 01:47:45 +09:00`
  - `docs(raw): widen source anchors through 3/17+ sessions`
  - surface 실험 전 기준점
- `B2 = d609f76`
  - `2026-04-18 02:28:27 +09:00`
  - `surface: replace hard-max progression merge with pooled blend`
  - 승인 없이 올라간 pooled-blend 실험
- `B3 = 03eb593`
  - `2026-04-18 03:17:08 +09:00`
  - `surface: make transverse component purely pooled`
  - 승인 없이 올라간 purely-pooled transverse 실험
- `B4 = c779121`
  - `2026-04-18 03:48:18 +09:00`
  - `surface: localize transverse reading around pooled progress`
  - 승인 없이 올라간 local-window transverse 실험
- `B5 = eb3022a`
  - `2026-04-18 04:03:00 +09:00`
  - `surface: make transverse guide-faithful`
  - 승인 없이 올라간 guide-faithful transverse 실험
- `B6 = ded4f59`
  - `2026-04-18 04:19:38 +09:00`
  - `surface: smooth guide-faithful transverse reading`
  - 승인 없이 올라간 smoothed guide-faithful transverse 실험
- `B7 = 57ee191`
  - `2026-04-18 04:39:26 +09:00`
  - `Revert "surface: localize transverse reading around pooled progress"`
  - `B2`~`B6` 계열 실험을 걷어낸 복귀 baseline
- `B8 = 23436f1`
  - `2026-04-18 05:04:20 +09:00`
  - `surface: drop transverse handoff smoothing`
  - `b3a4efa` 시절 수식 계열로 다시 맞춘 baseline
- `B9 = 1d9d102`
  - `2026-04-18 06:33:37 +09:00`
  - `surface: restore transverse handoff smoothing`
  - 사용자 승인 후 승격된 baseline
- `B10 = 2d9b99f`
  - `2026-04-18 14:48:19 +09:00`
  - `surface: use guide-center distance for transverse term`
  - 직전 baseline
- `B11 = 465398d`
  - `2026-04-18 16:18:52 +09:00`
  - `surface: use raw progression guide distance for transverse`
  - transverse object를 `raw visible progression guide polyline`까지의 최단거리로 단순화한 승인 baseline

## Discipline added from this point

- branch/split morphology 조사 중 baseline 후보는 `B{n}` 번호, commit hash, commit timestamp를 함께 기록한다.
- baseline으로 승인되어 승격하는 commit message subject에도 같은 번호를 `[B{n}]` 형태로 넣는다.
- 사용자 explicit approval 없이 `B{n+1}`을 `main` baseline으로 선언하거나 승격하지 않는다.
- docs-only/workflow commits는 baseline 번호에 넣지 않는다. baseline 번호는 behavior-changing surface baseline에만 쓴다.

## Open questions at the time

- branch/split morphology investigation에서 어떤 시점을 baseline 승격 후보로 부를 수 있는지
- explicit approval을 어떤 수준의 사용자 지시로 볼지
- historical comparison worktree를 언제 정리할지

## Later correction on the same date

- `B11 = 465398d`를 clean behavior baseline으로 둔 뒤, 그 위에서 별도 cleanup/adaptation batch를 승인했다.
- 이 후속 배치는 new baseline 승격이 아니라:
  - transverse public channel exactness 정리
  - generic adapter raw input 확장
  - current-truth docs/tests 이동
  를 한 번에 묶는 approved follow-up으로 취급한다.
- 사용자 intent는 raw adapter boundary를 `progression_supports`에만 고정하지 않고, 다음 precedence를 허용하는 쪽으로 좁혀졌다.
  - explicit `progression_supports`
  - `global_plan_supports`
  - bounded drivable-only reconstruction

## Raw update discipline added on the same date

- baseline 관련 raw note는 중요한 승인/교정이 생길 때 실시간에 가깝게 계속 갱신한다.
- baseline ledger는 approved baseline을 중심으로 누적한다.
  - `B{n} = <hash>`
  - baseline 한 줄 의미
- failed/intermediate experiment는 baseline 선택 맥락을 복원하는 데 필요한 정도로만 짧게 언급한다.
- baseline note는 과거 approved baseline도 계속 포함해 running ledger처럼 유지한다.
- repo-local guard와 local skill에도 같은 규칙을 같이 적어, branch/split morphology work에서 baseline 기록이 batch 밖으로 밀리지 않게 한다.

## Later follow-up on the same date

- `B11 = 465398d` 위에서 fragmented progression input normalization과 warning-level follow-up batch를 승인했다.
- 이 후속 배치는 new baseline 승격이 아니라 input-boundary cleanup으로 취급한다.
- 핵심 correction:
  - runtime formula는 `B11` 그대로 유지
  - `u_turn_many_small_progression_guides` 같은 obvious single-chain fragmentation은 runtime이 아니라 input normalization에서 canonical guide 하나로 접는다
  - explicit fragmented `progression_supports`는 여전히 upstream responsibility로 두되, adapter가 best-effort fallback을 시도하고 `progression_normalization` metadata에 provenance/severity를 남긴다
  - `global_plan_supports`와 drivable-derived progression은 adapter의 정상 canonicalization 입력으로 본다

## Later workflow correction on the same date

- normalization warning / target overlay 작업 중 unmerged fragmented-guide probe case를 `main`에 잠깐 올린 것은 승인 discipline miss였다.
- runtime baseline은 바꾸지 않았더라도, probe-only case나 probe-only loader behavior는 explicit approval 없이 `main`에 올리지 않는다.
- 이런 probe는 separate worktree나 explicitly approved case asset으로만 다뤄야 한다.
