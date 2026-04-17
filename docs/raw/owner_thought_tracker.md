# Owner Thought 변화 추적

이 문서는 사용자 원문 thought가 어떻게 바뀌었는지 추적하는 non-canonical 문서다. 원문 보존은 `notes/`가 담당하고, 최신 사용자 framing 요약은 [Owner Design Notebook](./owner_design_notebook.md)이 담당한다. 이 문서는 그 둘 사이에서 주제별 변화만 짧게 누적한다.

## longitudinal vs transverse weighting

### First raised

- 2026-04-17

### Current framing

- `transverse`가 corridor를 너무 강하게 붙잡기보다, `longitudinal`가 진행 선호를 더 강하게 줄 수 있다는 문제의식이 올라왔다.
- 이 아이디어는 단순 tuning보다 DPF가 어떤 종류의 preference field여야 하는지에 가깝다.

### Key changes by date

- 2026-04-17: 진행방향 성분이 메인으로 더 강해질 수 있다는 사용자 직관이 raw로 올라왔다.
- 2026-04-17: `normalized`는 계산을 막는 것이 아니라 visualization range를 다시 펴는 것이라는 구분이 대화에서 분리됐다.

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

## DPF as progress-preference device

### First raised

- 2026-04-17

### Current framing

- DPF는 입력 경로를 참고해 “어디로 가는 게 더 좋은지”를 bias로 주는 장치라는 framing이 사용자 쪽에서 분명하게 제안됐다.
- detailed path responsibility는 downstream planner/behavior가 더 많이 져야 한다는 문제의식이 같이 올라왔다.

### Key changes by date

- 2026-04-17: “진행 선호를 주는 장치”라는 한국어 framing이 초기 raw thought로 기록됐다.
- 2026-04-17: `corridor fidelity vs optimizer-upstream preference`보다 한국어 표현이 현재 의도를 더 잘 드러낸다는 판단이 대화에서 정리됐다.

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

### Linked raw notes

- [2026-04-17-raw-thought-capture-workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)

### Current status

- `partly reflected in canonical docs`

### Canonical docs touched (if any)

- `AGENTS.md`
- `docs/en/index.md`
- `docs/ko/index.md`
- `docs/en/explanation/documentation_writing_principles.md`
- `docs/ko/explanation/documentation_writing_principles.md`

### Open questions

- `.codex` backfill을 언제 어떤 단위로 갱신할지
- raw note에서 assistant context를 얼마나 자주 남길지
- raw surface를 future public portal에서 얼마나 노출할지
