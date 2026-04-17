# Owner Thought 변화 추적

이 문서는 사용자 원문 thought가 어떻게 바뀌었는지 추적하는 non-canonical 문서다. 원문 보존은 `notes/`가 담당하고, 최신 사용자 framing 요약은 [Owner Design Notebook](./owner_design_notebook.md)이 담당한다. 설계 발전 서사는 [Owner Design History](./owner_design_history.md)이 맡는다. 이 문서는 그 사이에서 형성과정 전체의 변화 지점을 짧게 누적한다.

## segment/index consumption and reachable progress

### First raised

- 2026-03-17

### Current framing

- progression을 node arrival event보다 작은 path piece의 consume로 읽는 직관이 가장 이르게 나왔다.
- 다음 노드로 바로 못 가더라도 갈 수 있는 곳까지는 계속 진행해야 한다는 reachable-progress 감각이 같이 붙었다.

### Key changes by date

- 2026-03-17: `노드 사이의 경로에 인덱스를 붙여서 소비`가 earliest form으로 제안됐다.
- 2026-03-17: `당장 다음 노드로 못가도 계속 갈 수 있는 길은 진행`이라는 reachable-progress 감각이 같이 올라왔다.
- 2026-03-17: user plan message에서 ordered segment path와 `current_segment_index` 소비 구조가 더 명시적으로 고정됐다.

### Linked raw notes

- [2026-03-17-segment-index-consumption-and-reachable-progress](./notes/2026-03-17-segment-index-consumption-and-reachable-progress.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- segment consumption을 DPF 입력 경로 역할의 기원으로 어디까지 끌어올릴지
- reachable progress를 이후 preference ordering으로 어떻게 일반화할지

## progression / gate intuition

### First raised

- 2026-03-17

### Current framing

- progression을 읽는 가장 단순한 규칙은 `게이트를 넘으면 다음으로 갈아탄다`는 기하학적 gate crossing이었다.
- 정상 범위 안에서 gate를 통과한 경우 기존 경로를 불필요하게 다시 만들지 않는다는 감각이 같이 올라왔다.

### Key changes by date

- 2026-03-17: `게이트를 지나면 다음 노드로 갈아타기`가 simplest progression rule로 제안됐다.
- 2026-03-17: `게이트 지나면 다음 노드`, `범위 내면 경로 수정 안함`이라는 식으로 규칙이 더 단순하게 다시 말해졌다.
- 2026-04-18: gate 직관을 DPF 설계 문서의 기원으로 다시 세우기로 결정했다.

### Linked raw notes

- [2026-03-17-progression-from-geometric-gate-intuition](./notes/2026-03-17-progression-from-geometric-gate-intuition.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- gate crossing이 이후 DPF progression semantics의 직접 정의가 될지
- gate와 consume을 pure geometry로 둘지, preference interpretation까지 끌어올릴지

## progress-first node progression and frontier priority

### First raised

- 2026-03-22

### Current framing

- gate consume만으로 진행이 멈추는 상황이 보이자, 못 가면 일단 멈추는 대신 갈 수 있는 frontier까지는 전진해야 한다는 pressure가 생겼다.
- 이 구간은 segment consume와 blocked frontier 전진을 분리해서 보게 만든 전환점이다.

### Key changes by date

- 2026-03-22: `장애물이 없다면 일단 진행은?`, `못가면 갈 수 있는곳까지 플래닝`이 제안됐다.
- 2026-03-22: `행동이 경로를 못잡아주고`라는 식으로 progression 정의와 behavior 책임이 연결돼 읽혔다.
- 2026-03-22: user plan message에서 `frontier-first blocked progression`이 고정되며, blocked case에서 frontier/local splice가 우선이라는 구조가 명시됐다.

### Linked raw notes

- [2026-03-22-progress-first-node-progression-and-frontier-priority](./notes/2026-03-22-progress-first-node-progression-and-frontier-priority.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- frontier-first 전진을 progression semantics의 일부로 볼지
- blocked case 전용 local rule로만 둘지

## local splice and lane corridor

### First raised

- 2026-03-17

### Current framing

- gate consume만으로 부족한 경우에는 전체 경로를 다시 만드는 것이 아니라 `ego -> next`까지만 다시 만드는 local splice가 맞다는 생각이 나왔다.
- 이 splice는 차선 범위 안에서만 허용해야 한다는 lane-range 직관이 같이 붙었다.

### Key changes by date

- 2026-03-17: `ego에서 다음 노드까지만 경로를 다시 만드는 방향`이 명시됐다.
- 2026-03-17: `범위는 차선범위`라는 제약이 바로 붙었다.
- 2026-03-22: frontier-first blocked progression이 나오면서 local splice는 normal progression과 분리된 blocked-case rule로 더 선명해졌다.

### Linked raw notes

- [2026-03-17-local-splice-and-lane-range](./notes/2026-03-17-local-splice-and-lane-range.md)
- [2026-03-22-progress-first-node-progression-and-frontier-priority](./notes/2026-03-22-progress-first-node-progression-and-frontier-priority.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- local splice를 DPF 설계의 핵심 비유로 둘지
- blocked-case fallback으로만 둘지

## segment-first global path contract and visualization

### First raised

- 2026-03-17

### Current framing

- segment consumption을 behavior 내부 해석으로만 두기보다, 전역 경로를 처음부터 ordered segment path로 두는 쪽이 더 맞다는 생각으로 발전했다.
- node/edge/gate/range를 함께 시각화해야 progression contract를 디버깅할 수 있다는 요구도 같이 올라왔다.

### Key changes by date

- 2026-03-17: `전역 경로를 생성할 때부터 세그먼트들로`라는 제안이 나왔다.
- 2026-03-17: `인덱스와 노드를 소비`, `노드랑 간선형태` 시각화 요구가 같이 붙었다.
- 2026-03-17: user plan message에서 ordered segment contract와 visualization spine이 더 강하게 고정됐다.

### Linked raw notes

- [2026-03-17-segment-first-global-path-contract-and-visualization](./notes/2026-03-17-segment-first-global-path-contract-and-visualization.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- 이 contract를 DPF 입력 경로 역할 설명으로 얼마나 끌어올릴지
- visualization choice와 conceptual contract를 어디까지 분리할지

## docs-first reset and canonical semantics

### First raised

- 2026-04-09

### Current framing

- 구현 이관보다 문서와 철학을 먼저 잠그는 docs-first reset이 필요하다는 생각이 명시됐다.
- canonical 입력은 `주행 가능 의미 + 진행 의미`로 두고, 선호는 입력이 아니라 field 구조가 만든다는 가설이 더 분명하게 고정됐다.

### Key changes by date

- 2026-04-09: 새 repo로 옮기더라도 문서와 생각 철학만 가져가서 다시 세우는 쪽이 낫다는 판단이 나왔다.
- 2026-04-09: `Docs-First 재시작 계획`으로 문서 중심 restart가 plan message로 고정됐다.
- 2026-04-09: `전체 문서 정리 계획`에서 `주행 가능 의미 + 진행 의미`, `선호는 입력이 아니라 field 구조가 생성한다`가 canonical 축으로 다시 고정됐다.

### Linked raw notes

- [2026-04-09-docs-first-reset-and-canonical-semantics](./notes/2026-04-09-docs-first-reset-and-canonical-semantics.md)

### Current status

- `partly reflected in canonical docs`

### Canonical docs touched (if any)

- `README.md`
- `docs/en/explanation/project_overview.md`
- `docs/en/explanation/base_field_foundation.md`
- `docs/en/reference/input_semantics.md`

### Open questions

- docs-first reset에서 고정한 언어가 이후 구현 drift를 얼마나 잘 막는지
- SSC와 canonical definition 사이의 거리를 장기적으로 어떻게 유지할지

## progress-tilted score space and layer separation

### First raised

- 2026-04-09

### Current framing

- DPF/score field의 본체는 path generator가 아니라, 진행방향으로 기울어진 score space에 더 가깝다는 raw 설명이 나왔다.
- exception은 base score space 위에 얹히는 다른 layer로 봐야 하며, 단순 additive costmap처럼 섞으면 안 된다는 경계가 같이 올라왔다.

### Key changes by date

- 2026-04-09: `중력장처럼 돼있는 공간`, `진행방향으로 기울어진 점수 공간`이라는 원문 설명이 나왔다.
- 2026-04-09: base score space와 costmap/other layers 분리를 explicit하게 말했다.
- 2026-04-09: `선호는 우리가 정하는게 아니라 ... 그 구조가 만들어 준다`는 가설이 더 직접적으로 표현됐다.

### Linked raw notes

- [2026-04-09-progress-tilted-score-space-and-layer-separation](./notes/2026-04-09-progress-tilted-score-space-and-layer-separation.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- 이 object를 preference field, score function, goal cost function 중 어떤 언어로 설명할지
- layer separation을 canonical에서 어디까지 구조로 고정할지

## whole-space fabric instead of tube support

### First raised

- 2026-04-09

### Current framing

- score space는 guide 주변의 tube support band가 아니라 공간 전체가 기울어진 fabric에 가까워야 한다는 objection이 raw로 나왔다.
- branch/merge에서 빈 공간이 생기지 않는 연속 surface 직관이 여기서 더 직접적으로 나타났다.

### Key changes by date

- 2026-04-09: `애초에 공간이라니까`, `복소공간 스프링`, `염소뿔 사이를 메운 느낌`, `꽈배기` 같은 표현으로 whole-space image가 강조됐다.
- 2026-04-09: tube-like score support와 seam에 대한 불만이 explicit하게 제기됐다.
- 2026-04-09: `Tube Field 제거와 Whole-Fabric Progression Space` plan message가 current implementation 전환으로 고정됐다.

### Linked raw notes

- [2026-04-09-whole-space-fabric-instead-of-tube-support](./notes/2026-04-09-whole-space-fabric-instead-of-tube-support.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- whole-space fabric intuition을 exact math 없이 어디까지 canonical로 말할 수 있는지
- branch overlap과 smoothness를 어디까지 허용할지

## semantic snapshot / query context / score-function framing

### First raised

- 2026-04-10

### Current framing

- local map의 의미 자체와 평가 시점의 문맥을 분리해야 한다는 생각이 `Semantic Input Snapshot`과 `Query Context`라는 형태로 더 선명해졌다.
- 이 시점에는 SSC-specific naming을 canonical truth로 올리지 않고, meaning translator only, local window experimental, branch winner not fixed라는 boundary도 같이 잠겼다.

### Key changes by date

- 2026-04-10: long-form user message에서 `의미번역기만`, `ego_pose는 최소 필수 출력이 아님`, `local map 범위는 실험 영역`, `branch winner는 canonical에서 정하지 않음`, `SSC에 매몰되면 안됨`이 한 번에 정리됐다.
- 2026-04-10: `Semantic Input Snapshot` / `Query Context` 표 구성이 raw anchor로 올라왔다.
- 2026-04-10: `선호장`, `score function`, `goal cost function` 언어 선택에 대한 질문이 explicit하게 나왔다.

### Linked raw notes

- [2026-04-10-semantic-snapshot-query-context-and-score-function](./notes/2026-04-10-semantic-snapshot-query-context-and-score-function.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- `score function` 언어가 사용자의 원래 의도와 얼마나 맞는지
- `Query Context`와 field generator 경계를 얼마나 강하게 고정할지

## DPF as progress-preference device

### First raised

- 2026-04-17

### Current framing

- DPF는 입력 경로를 참고해 “어디로 가는 게 더 좋은지”를 bias로 주는 장치라는 framing이 사용자 쪽에서 분명하게 제안됐다.
- detailed path responsibility는 downstream planner/behavior가 더 많이 져야 한다는 문제의식이 같이 올라왔다.

### Key changes by date

- 2026-04-17: “진행 선호를 주는 장치”라는 한국어 framing이 raw thought로 기록됐다.
- 2026-04-17: `corridor fidelity vs optimizer-upstream preference`보다 한국어 표현이 현재 의도를 더 잘 드러낸다는 판단이 대화에서 정리됐다.
- 2026-04-18: 입력 경로를 그대로 복제해야 하는 경로라기보다, 어디로 가는 게 더 좋은지 판단할 때 참고하는 기준으로 보는 쪽으로 설계 정리가 더 좁혀졌다.

### Linked raw notes

- [2026-04-17-dpf-as-progress-preference-device](./notes/2026-04-17-dpf-as-progress-preference-device.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- progress-preference language를 canonical explanation으로 언제 올릴지
- reverse bias를 같은 틀 안에서 어떻게 설명할지

## longitudinal vs transverse weighting

### First raised

- 2026-04-17

### Current framing

- `transverse`가 corridor를 강하게 붙잡는 주역이기보다, `longitudinal`가 진행 선호를 더 직접적으로 주는 주역이 될 수 있다는 문제의식이 나왔다.
- 이 주제는 단순 tuning이 아니라 DPF가 어떤 종류의 preference field여야 하는지와 연결된다.

### Key changes by date

- 2026-04-17: 진행방향 성분이 메인으로 더 강해질 수 있다는 사용자 직관이 raw로 올라왔다.
- 2026-04-17: `Normalized`는 계산을 막는 것이 아니라 visualization range를 다시 펴는 것이라는 구분이 같이 정리됐다.
- 2026-04-18: 이 주제는 tuning보다 DPF object definition 문제라는 쪽이 더 분명해졌다.

### Linked raw notes

- [2026-04-17-longitudinal-vs-transverse-weighting](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- corridor fidelity를 어디까지 base field가 책임져야 하는가
- longitudinal dominance를 언제 current design belief로 올릴지

## simulator comparison methodology and MPPI tuning

### First raised

- 2026-04-18

### Current framing

- DPF 비교는 하나의 승패 표로 끝나는 것이 아니라, 공정한 real-time benchmark, 구조 비용 benchmark, tuning frontier를 분리해서 봐야 한다는 문제의식이 나왔다.
- MPPI budget과 control frequency를 어떻게 다루는지 자체가 설계와 평가의 일부라는 생각이 올라왔다.

### Key changes by date

- 2026-04-18: `mppi를 얼마나 최적화 할 수 있는지`도 같이 보고 싶다는 요청이 나왔다.
- 2026-04-18: `Hz를 못 올린다고 그냥 낮춰서 비교하면 제대로 된 실험이 아니다`라는 우려가 raw로 올라왔다.
- 2026-04-18: real-time constrained benchmark / fixed-budget benchmark / tuning frontier study를 분리하는 방법론이 잠겼다.

### Linked raw notes

- [2026-04-18-simulator-comparison-methodology-and-mppi-tuning](./notes/2026-04-18-simulator-comparison-methodology-and-mppi-tuning.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- tuned target profile을 어느 숫자로 잠글지
- DPF 평가 문서에서 이 benchmark split을 언제 canonical evaluation guidance로 올릴지

## raw thought capture workflow

### First raised

- 2026-04-17

### Current framing

- 사용자 채팅 원문 자체를 보존하는 raw surface와, 아이디어 변화를 추적하는 누적 문서를 분리해 두는 workflow가 필요하다는 제안이 올라왔다.
- `.codex` session/history는 source material로 쓰되, raw note보다 앞서 나가는 derived docs를 만들면 안 된다는 notes-first rule이 뒤따랐다.

### Key changes by date

- 2026-04-17: 날짜별 raw note + 하나의 변화 추적 문서 구조가 제안됐다.
- 2026-04-17: raw에는 사용자 원문 발췌를 우선하고, assistant 맥락은 필요할 때만 분리해서 넣는 쪽으로 좁혀졌다.
- 2026-04-18: `owner_design_notebook`과 `owner_design_history`도 notes를 먼저 넓힌 뒤 갱신해야 한다는 anchor-first rule이 더 분명해졌다.

### Linked raw notes

- [2026-04-17-raw-thought-capture-workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)

### Current status

- `partly reflected in canonical docs`

### Canonical docs touched (if any)

- `AGENTS.md`
- `docs/raw/README.md`
- `docs/en/explanation/documentation_writing_principles.md`
- `docs/ko/explanation/documentation_writing_principles.md`

### Open questions

- active session later segment가 materialize된 뒤 source 표기를 언제 갱신할지
- raw note를 언제 broad source reread로 다시 열어야 하는지

## owner design document shape

### First raised

- 2026-04-18

### Current framing

- raw note와 tracker만으로는 부족하고, 최신 사용자 설계 thinking을 바로 읽을 수 있는 clean design prose와 설계 발전 history prose가 별도로 필요하다는 요구가 분명해졌다.
- 동시에 그런 파생 문서도 notes보다 앞서 나가면 안 된다는 기준이 같이 생겼다.

### Key changes by date

- 2026-04-18: `설계 문서는 메타 없이 깔끔하게`라는 요구가 explicit하게 나왔다.
- 2026-04-18: latest design notebook과 design history를 분리하는 구조가 잠겼다.
- 2026-04-18: notes가 충분치 않으면 derived docs가 얇아지거나 오염된다는 지적이 나왔고, full source reread를 통해 raw anchor를 다시 넓히는 방향으로 전환했다.

### Linked raw notes

- [2026-04-18-owner-design-doc-shape-and-backfill](./notes/2026-04-18-owner-design-doc-shape-and-backfill.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- latest design notebook을 어느 정도 길이로 유지할지
- design history에 버려진 생각을 어느 밀도로 남길지

## branch/split baseline promotion discipline

### First raised

- 2026-04-18

### Current framing

- branch/split morphology investigation은 historical snapshot, fixture variant, transverse 실험이 빠르게 겹치기 때문에 baseline discipline이 쉽게 무너진다.
- 실험 상태를 `main`이나 baseline으로 승격하는 일은 explicit user approval이 있어야 하고, 그 전에는 separate worktree에만 남겨야 한다.

### Key changes by date

- 2026-04-18: user가 `분기 시작하고 나서 더러워진 것`과 `승인 안 하고 baseline으로 올린 것`을 직접 연결해 지적했다.
- 2026-04-18: local skill에 branch/split investigation 동안에는 explicit approval 없이 baseline/main 승격을 금지하는 guardrail을 추가했다.

### Linked raw notes

- [2026-04-18-branch-split-baseline-approval-discipline](./notes/2026-04-18-branch-split-baseline-approval-discipline.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- 같은 rule을 repo-local AGENTS까지 올릴지
- abandoned experiment worktree를 언제 cleanup해야 하는지
