# Owner Thought 변화 추적

이 문서는 사용자 원문 thought가 어떻게 바뀌었는지 추적하는 non-canonical 문서다. 원문 보존은 `notes/`가 담당하고, 최신 사용자 framing 요약은 [Owner Design Notebook](./owner_design_notebook.md)이 담당한다. 이 문서는 그 둘 사이에서 현재 세션 안의 변화 순서를 짧게 누적한다.

## progression / gate intuition

### First raised

- 2026-03-17

### Current framing

- progression을 읽는 가장 이른 직관은 `게이트를 넘으면 다음으로 갈아탄다`는 식의 기하학적 gate crossing이다.
- 정상 범위에서 gate를 넘으면 경로를 다시 만들지 않고 consume하고 넘어가고, local splice는 막혔을 때만 쓰는 조각이라는 생각이 먼저 나왔다.

### Key changes by date

- 2026-03-17: `게이트를 지나면 다음 노드로 갈아타기`가 simplest progression rule로 제안됐다.
- 2026-03-17: `게이트 근처 arm`보다 `gate crossing only + 간단한 보호조건`이 더 단순하고 자연스럽다는 방향이 정리됐다.
- 2026-03-17: 정상 범위 gate 통과 시에는 경로를 수정하지 않고, 막힌 경우에만 local splice를 쓰는 구분이 명시됐다.
- 2026-04-18: 이 gate 직관을 DPF 설계 문서의 출발점으로 다시 세우기로 결정했다.

### Linked raw notes

- [2026-03-17-progression-from-geometric-gate-intuition](./notes/2026-03-17-progression-from-geometric-gate-intuition.md)

### Current status

- `under discussion`

### Canonical docs touched (if any)

- 없음

### Open questions

- gate crossing 직관을 DPF의 progression 정의로 얼마나 직접 연결할지
- gate consume intuition과 whole-space preference field를 어떤 수준에서 연결할지

## DPF as progress-preference device

### First raised

- 2026-04-17

### Current framing

- DPF는 입력 경로를 참고해 “어디로 가는 게 더 좋은지”를 bias로 주는 장치라는 framing이 사용자 쪽에서 분명하게 제안됐다.
- detailed path responsibility는 downstream planner/behavior가 더 많이 져야 한다는 문제의식이 같이 올라왔다.

### Key changes by date

- 2026-03-17: gate를 넘으면 다음으로 갈아타는 단순 progression intuition이 먼저 나타났다.
- 2026-04-17: “진행 선호를 주는 장치”라는 한국어 framing이 초기 raw thought로 기록됐다.
- 2026-04-17: `corridor fidelity vs optimizer-upstream preference`보다 한국어 표현이 현재 의도를 더 잘 드러낸다는 판단이 대화에서 정리됐다.
- 2026-04-18: 입력 경로는 reference spine이지 그대로 복제할 궤적은 아니라는 쪽으로 설계 정리가 더 좁혀졌다.

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

- 2026-03-17: progression을 gate crossing으로 단순화하는 직관이 먼저 나왔고, 이는 나중의 longitudinal 중심 문제의식의 앞단에 놓이게 됐다.
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
