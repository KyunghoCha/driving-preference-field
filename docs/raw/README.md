# Raw Owner Thought Notes

이 폴더는 사용자 원문 생각과 최신 사용자 설계 thinking을 보존하는 Korean-first raw surface다.

여기 문서는 **non-canonical**이다. 현재 truth, 구현 계약, phase 상태, user-facing semantics는 계속 `docs/en|ko/explanation/`, `reference/`, `how-to/`, `status/`에서만 고정한다. `docs/raw/`는 그 canonical 문서를 대체하지 않고, owner-origin source material과 변화 추적을 보존하는 층으로만 유지한다.

## structure

- `notes/`
  - 사용자 채팅 원문에서 repo-level idea, design intuition, workflow thought를 verbatim에 가깝게 발췌해 남긴다.
  - assistant 내용은 맥락 복원이 꼭 필요할 때만 별도 블록으로 분리한다.
- [Owner Thought 변화 추적](./owner_thought_tracker.md)
  - 아이디어가 언제 어떻게 바뀌었는지 주제별로 짧게 누적한다.
- [Owner Design Notebook](./owner_design_notebook.md)
  - raw나 tracker를 읽지 않아도 최신 사용자 설계 생각을 한 번에 파악할 수 있게, 메타를 줄인 clean design prose로 정리한다.

## source policy

- raw note의 기본 source는 사용자 채팅 원문 verbatim 발췌다.
- 가능하면 `session id`, `session date`, `$HOME/.codex/...` 기준 source location을 함께 적는다.
- active session이 아직 `$HOME/.codex/sessions/...`에 materialize되지 않았다면, 그 상태를 note에 명시하고 현재 thread context를 source로 쓴다.
- `.codex` 로그 전체를 문서에 복사하지 않는다. 필요한 발췌만 남긴다.
- `1번`, `2번`, `그거`, `이거`, `저거`처럼 referential fragment가 나오면, 해당 지시 대상을 복원할 수 있도록 앞뒤 사용자 메시지도 함께 발췌한다.
- historical backfill은 `.codex` 세션을 넓게 검토하되, DPF thought에 실질적으로 기여한 것으로 확신할 수 있는 대화만 올린다.

## boundary

- current implementation을 정의하지 않는다.
- canonical contract나 public claim을 직접 바꾸지 않는다.
- EN/KO parity 대상이 되지 않는다.

현재 포함된 raw note:

- [2026-04-17-longitudinal-vs-transverse-weighting](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)
- [2026-04-17-dpf-as-progress-preference-device](./notes/2026-04-17-dpf-as-progress-preference-device.md)
- [2026-04-17-raw-thought-capture-workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)
- [2026-04-18-owner-design-doc-shape-and-backfill](./notes/2026-04-18-owner-design-doc-shape-and-backfill.md)
