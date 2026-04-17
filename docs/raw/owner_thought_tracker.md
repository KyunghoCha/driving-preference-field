# Owner Thought 변화 추적

이 문서는 사용자 원문 thought가 어떻게 바뀌었는지 추적하는 non-canonical 문서다. 원문 보존은 `notes/`가 담당하고, 최신 사용자 framing 요약은 [Owner Design Notebook](./owner_design_notebook.md)이 담당한다. 설계 발전 서사는 [Owner Design History](./owner_design_history.md)이 맡는다. 이 문서는 그 둘 사이에서 현재 세션 안의 변화 순서를 짧게 누적한다.

## segment/index consumption and reachable progress

### First raised

- 2026-03-17

### Current framing

- progression을 처음부터 노드 도달 사건으로 보기보다, 작은 path piece에 인덱스를 붙여 consume하는 방식으로 읽으려는 생각이 먼저 나왔다.
- 다음 노드로 바로 못 가더라도 갈 수 있는 데까지는 계속 진행해야 한다는 reachable-progress 감각이 같이 올라왔다.

### Key changes by date

- 2026-03-17: `노드 사이의 경로에 인덱스를 붙여서 소비`가 가장 이른 형태로 제안됐다.
- 2026-03-17: `당장 다음 노드로 못가도 계속 갈 수 있는 길은 진행`이라는 직관이 같이 올라왔다.
- 2026-03-17: 사용자 plan 메시지에서 ordered segment path와 `current_segment_index` 소비 구조가 더 명시적으로 고정됐다.

### Linked raw notes

- [2026-03-17-segment-index-consumption-and-reachable-progress](./notes/2026-03-17-segment-index-consumption-and-reachable-progress.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- reachable progress를 DPF progression과 어떤 수준에서 연결할지
- segment consumption을 path-reading intuition으로만 둘지, 더 일반적인 field semantics로 올릴지

## progression / gate intuition

### First raised

- 2026-03-17

### Current framing

- progression을 읽는 가장 이른 단순화는 `게이트를 넘으면 다음으로 갈아탄다`는 식의 기하학적 gate crossing이다.
- 범위 안에서 gate를 통과했으면 기존 경로를 불필요하게 다시 만들지 않고 그대로 유지하거나 consume하고 넘어가야 한다는 생각이 같이 따라왔다.

### Key changes by date

- 2026-03-17: `게이트를 지나면 다음 노드로 갈아타기`가 simplest progression rule로 제안됐다.
- 2026-03-17: `게이트 지나면 다음 노드`, `범위 내면 경로 수정 안함`이라는 식으로 조건이 더 단순하게 재말해졌다.
- 2026-03-17: `범위 내에서 gate를 통과하면 기존 경로 유지`를 다시 확인하는 사용자 질문이 나왔다.
- 2026-04-18: 이 gate 직관을 DPF 설계 문서의 출발점으로 다시 세우기로 결정했다.

### Linked raw notes

- [2026-03-17-progression-from-geometric-gate-intuition](./notes/2026-03-17-progression-from-geometric-gate-intuition.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- gate crossing 직관을 DPF의 progression 정의로 얼마나 직접 연결할지
- gate 범위와 consume을 pure geometry로 둘지, preference interpretation까지 올릴지

## local splice and lane corridor

### First raised

- 2026-03-17

### Current framing

- gate consume만으로 부족한 경우에는 전체 경로를 다시 만드는 것이 아니라 `ego -> next`까지만 다시 만드는 local splice가 맞다는 생각이 나왔다.
- 이 splice는 차선 범위 안에서만 허용해야 한다는 lane-range 직관이 같이 붙었다.

### Key changes by date

- 2026-03-17: `ego에서 다음 노드까지만 경로를 다시 만드는 방향`이 명시됐다.
- 2026-03-17: `범위는 차선범위`라는 제약이 바로 붙었다.
- 2026-03-17: 사용자 plan 메시지에서 `ego -> current exit node` local splice와 차선 corridor 조건이 더 명시적으로 고정됐다.

### Linked raw notes

- [2026-03-17-local-splice-and-lane-range](./notes/2026-03-17-local-splice-and-lane-range.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- local splice를 DPF 설계의 핵심으로 볼지, blocked-case fallback으로 둘지
- lane range를 structure-preserving prior로 읽을지, execution-side safety boundary로 읽을지

## segment-first global path contract

### First raised

- 2026-03-17

### Current framing

- segment consumption을 behavior 내부 해석으로만 두기보다, 전역 경로를 처음부터 ordered segment path로 두는 쪽이 더 맞다는 생각으로 발전했다.
- 이 전환과 함께 노드/간선을 명시적으로 시각화해야 한다는 요구도 같이 올라왔다.

### Key changes by date

- 2026-03-17: `전역 경로를 생성할 때부터 세그먼트들로`라는 제안이 나왔다.
- 2026-03-17: `인덱스와 노드를 소비`, `노드랑 간선형태` 시각화 요구가 같이 붙었다.
- 2026-03-17: 사용자 plan 메시지에서 global planner가 ordered segment sequence를 발행하고 behavior가 그것을 소비하는 구조가 더 강하게 고정됐다.
- 2026-03-17: node visualization은 점이어도 되지만 결국 arrow가 더 낫다는 취향 조정이 뒤따랐다.

### Linked raw notes

- [2026-03-17-segment-first-global-path-contract-and-visualization](./notes/2026-03-17-segment-first-global-path-contract-and-visualization.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- 이 전환을 DPF 쪽에서 metaphor로만 둘지, 입력 경로 역할 정의에 더 직접 반영할지
- visualization choice와 conceptual contract를 어디까지 분리할지

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

- downstream planner와 base field의 책임 경계를 어디까지 나눌지
- 후진/반대 진행 방향 bias를 같은 틀에서 설명할지
- canonical explanation 문서에 언제 반영할지

## longitudinal vs transverse weighting

### First raised

- 2026-04-17

### Current framing

- `transverse`가 corridor를 너무 강하게 붙잡기보다, `longitudinal`가 진행 선호를 더 강하게 줄 수 있다는 문제의식이 올라왔다.
- 이 아이디어는 단순 tuning보다 DPF가 어떤 종류의 preference field여야 하는지에 가깝다.

### Key changes by date

- 2026-04-17: 진행방향 성분이 메인으로 더 강해질 수 있다는 사용자 직관이 raw로 올라왔다.
- 2026-04-17: `normalized`는 계산을 막는 것이 아니라 visualization range를 다시 펴는 것이라는 구분이 대화에서 분리됐다.
- 2026-04-18: 이 주제는 단순 tuning보다 DPF가 어떤 종류의 preference field인지 묻는 설계 문제라는 방향이 더 분명해졌다.

### Linked raw notes

- [2026-04-17-longitudinal-vs-transverse-weighting](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- base field가 corridor fidelity를 얼마나 강하게 책임져야 하는가
- `longitudinal_gain` 조정은 tuning 문제인가, object-definition 문제인가
- `Fixed` vs `Normalized` scale 비교를 canonical guide에 올릴 가치가 있는가

## raw thought capture workflow

### First raised

- 2026-04-17

### Current framing

- 사용자 채팅 원문 자체를 보존하는 raw surface와, 아이디어 변화를 추적하는 누적 문서를 분리해 두는 workflow가 필요하다는 제안이 올라왔다.
- `.codex` session/history는 source material로 쓰되, canonical truth나 raw note 자체와는 구분한다.

### Key changes by date

- 2026-04-17: 날짜별 raw note + 하나의 변화 추적 문서 구조가 제안됐다.
- 2026-04-17: raw에는 사용자 원문 발췌를 우선하고, assistant 맥락은 필요할 때만 분리해서 넣는 쪽으로 좁혀졌다.
- 2026-04-17: `.codex` 기록을 source로 확인하되, 전체 로그를 복사하지 않는다는 boundary가 정리됐다.
- 2026-04-18: raw/tracker와 별도로, 메타를 줄인 clean design prose 문서가 필요하다는 요구가 분명해졌다.
- 2026-04-18: 사용자가 current active thread 자체를 authoritative source로 지정했고, broad historical archaeology보다 current active thread + confirmed materialized cluster를 우선하는 방향으로 다시 잠갔다.

### Linked raw notes

- [2026-04-17-raw-thought-capture-workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)
- [2026-04-18-owner-design-doc-shape-and-backfill](./notes/2026-04-18-owner-design-doc-shape-and-backfill.md)

### Current status

- `partly reflected in canonical docs`

### Canonical docs touched (if any)

- `AGENTS.md`
- `docs/en/index.md`
- `docs/ko/index.md`
- `docs/en/explanation/documentation_writing_principles.md`
- `docs/ko/explanation/documentation_writing_principles.md`

### Open questions

- active thread later segment가 materialize된 뒤 source 표기를 언제 갱신할지
- raw note에서 assistant context를 얼마나 자주 남길지
- raw surface를 future public portal에서 얼마나 노출할지

## owner design document shape

### First raised

- 2026-04-18

### Current framing

- `owner_design_notebook.md`는 notebook-style metadata 문서가 아니라, raw/notes를 기준으로 최신 사용자 설계 생각을 clean prose로 정리하는 설계 문서처럼 읽혀야 한다.
- raw와 tracker가 메타와 이력을 맡고, design 문서는 최신 thinking을 개념적으로 정리하는 역할을 맡는다.

### Key changes by date

- 2026-04-18: 설계 문서에는 메타 필드보다 설계 내용 자체가 전면에 와야 한다는 요구가 명시됐다.
- 2026-04-18: raw/tracker/design의 3층 역할 분리가 guard와 docs wording에까지 반영되기 시작했다.
- 2026-04-18: design 문서는 raw/notes를 기준으로 해야 하고, 현재 세션 대화를 authoritative source로 삼아 다시 정리해야 한다는 방향이 명시됐다.

### Linked raw notes

- [2026-04-18-owner-design-doc-shape-and-backfill](./notes/2026-04-18-owner-design-doc-shape-and-backfill.md)

### Current status

- `partly reflected in canonical docs`

### Canonical docs touched (if any)

- `AGENTS.md`
- `docs/en/index.md`
- `docs/ko/index.md`
- `docs/en/explanation/documentation_writing_principles.md`
- `docs/ko/explanation/documentation_writing_principles.md`

### Open questions

- design 문서가 explanation-like prose를 유지하면서도 raw를 얼마나 직접적으로 반영해야 하는지
- 이후 canonical docs로 올라갈 때 어떤 경계에서 번역/정제가 필요한지
