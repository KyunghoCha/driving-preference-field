# Raw Owner Thought Notes

이 폴더는 사용자 원문 생각과 최신 사용자 설계 thinking을 보존하는 Korean-first raw surface다.

여기 문서는 **non-canonical**이다. 현재 truth, 구현 계약, phase 상태, user-facing semantics는 계속 `docs/en|ko/explanation/`, `reference/`, `how-to/`, `status/`에서만 고정한다. `docs/raw/`는 그 canonical 문서를 대체하지 않고, owner-origin source material과 변화 추적을 보존하는 층으로만 유지한다.

## structure

- `notes/`
  - 사용자 채팅 원문에서 repo-level idea, design intuition, workflow thought를 verbatim에 가깝게 발췌해 남긴다.
  - assistant 내용은 맥락 복원이 꼭 필요할 때만 별도 블록으로 분리한다.
  - 설계 전환을 실제로 고정한 사용자 plan 메시지(`PLEASE IMPLEMENT THIS PLAN` 등)도 raw anchor로 포함할 수 있다.
- [Owner Thought 변화 추적](./owner_thought_tracker.md)
  - `notes/`에 있는 anchor를 기준으로, 아이디어가 언제 어떻게 바뀌었는지 주제별로 짧게 누적한다.
- [Owner Design History](./owner_design_history.md)
  - 문제 인식부터 현재까지 설계 생각이 어떤 전환점을 거쳐 형성됐는지, notes-grounded clean history prose로 핵심 이정표만 남긴다.
- [Owner Design Notebook](./owner_design_notebook.md)
  - `notes/`를 읽지 않아도 최신 사용자 설계 생각을 한 번에 파악할 수 있게, notes-grounded clean design prose로 정리한다.

## source policy

- raw note의 기본 source는 사용자 채팅 원문 verbatim 발췌다.
- 가능하면 `session id`, `session date`, `$HOME/.codex/...` 기준 source location을 함께 적는다.
- active session이 아직 `$HOME/.codex/sessions/...`에 materialize되지 않았다면, 그 상태를 note에 명시하고 current active thread context를 source로 쓴다.
- 사용자가 현재 active thread를 authoritative source로 지정하면, speculative historical `.codex` archaeology보다 current active thread와 confirmed materialized cluster를 먼저 쓴다.
- 사용자가 더 넓은 materialized source window를 명시적으로 지정하면, 기존 요약 문서보다 그 source set 전체를 다시 읽고 `notes/`를 먼저 넓힌 뒤 파생 문서를 갱신한다.
- `.codex` 로그 전체를 문서에 복사하지 않는다. 필요한 발췌만 남긴다.
- `1번`, `2번`, `그거`, `이거`, `저거`처럼 referential fragment가 나오면, 해당 지시 대상을 복원할 수 있도록 앞뒤 사용자 메시지도 함께 발췌한다.
- wider historical backfill은 별도 배치에서만 하고, source confidence가 낮으면 올리지 않는다.
- 파생 문서는 `notes/`보다 앞서 나가면 안 된다. `owner_thought_tracker.md`, `owner_design_history.md`, `owner_design_notebook.md`는 모두 `notes/`를 먼저 갱신한 뒤 `tracker -> history -> latest design notebook` 순서로 따라간다.

## boundary

- current implementation을 정의하지 않는다.
- canonical contract나 public claim을 직접 바꾸지 않는다.
- EN/KO parity 대상이 되지 않는다.
- 최신 설계 정리는 `owner_design_notebook.md`, 설계 발전 서사는 `owner_design_history.md`가 맡는다.

현재 포함된 raw note:

- [2026-03-17-progression-from-geometric-gate-intuition](./notes/2026-03-17-progression-from-geometric-gate-intuition.md)
- [2026-03-17-segment-index-consumption-and-reachable-progress](./notes/2026-03-17-segment-index-consumption-and-reachable-progress.md)
- [2026-03-17-local-splice-and-lane-range](./notes/2026-03-17-local-splice-and-lane-range.md)
- [2026-03-17-segment-first-global-path-contract-and-visualization](./notes/2026-03-17-segment-first-global-path-contract-and-visualization.md)
- [2026-03-22-progress-first-node-progression-and-frontier-priority](./notes/2026-03-22-progress-first-node-progression-and-frontier-priority.md)
- [2026-04-09-docs-first-reset-and-canonical-semantics](./notes/2026-04-09-docs-first-reset-and-canonical-semantics.md)
- [2026-04-09-progress-tilted-score-space-and-layer-separation](./notes/2026-04-09-progress-tilted-score-space-and-layer-separation.md)
- [2026-04-09-whole-space-fabric-instead-of-tube-support](./notes/2026-04-09-whole-space-fabric-instead-of-tube-support.md)
- [2026-04-10-semantic-snapshot-query-context-and-score-function](./notes/2026-04-10-semantic-snapshot-query-context-and-score-function.md)
- [2026-04-17-longitudinal-vs-transverse-weighting](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)
- [2026-04-17-dpf-as-progress-preference-device](./notes/2026-04-17-dpf-as-progress-preference-device.md)
- [2026-04-17-raw-thought-capture-workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)
- [2026-04-18-owner-design-doc-shape-and-backfill](./notes/2026-04-18-owner-design-doc-shape-and-backfill.md)
- [2026-04-18-simulator-comparison-methodology-and-mppi-tuning](./notes/2026-04-18-simulator-comparison-methodology-and-mppi-tuning.md)
