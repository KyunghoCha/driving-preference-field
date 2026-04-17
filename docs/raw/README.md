# Raw Owner Thought Notes

이 폴더는 사용자 원문 생각을 보존하는 Korean-first raw surface다.

여기 문서는 **non-canonical**이다. 현재 truth, 구현 계약, phase 상태, user-facing semantics는 계속 `docs/en|ko/explanation/`, `reference/`, `how-to/`, `status/`에서만 고정한다. `docs/raw/`는 그 canonical 문서를 대체하지 않고, owner-origin source material과 변화 추적을 보존하는 층으로만 유지한다.

## 이 폴더가 하는 일

- 사용자 채팅 원문에서 repo-level idea, design intuition, workflow thought를 발췌해 남긴다.
- 필요하면 assistant 답변도 맥락용으로 남기되, 사용자 원문과 섞지 않고 별도 블록으로 명시한다.
- 아이디어가 언제 어떻게 바뀌었는지 추적할 수 있게 raw note와 변화 추적 문서를 함께 유지한다.

## 이 폴더가 하지 않는 일

- current implementation을 정의하지 않는다.
- canonical contract나 public claim을 직접 바꾸지 않는다.
- EN/KO parity 대상이 되지 않는다.

## source policy

- raw note의 기본 source는 사용자 채팅 원문 verbatim 발췌다.
- 가능하면 `session id`, `session date`, `$HOME/.codex/...` 기준 source location을 함께 적는다.
- active session이 아직 `$HOME/.codex/sessions/...`에 materialize되지 않았다면, 그 상태를 note에 명시하고 현재 thread context를 source로 쓴다.
- `.codex` 로그 전체를 문서에 복사하지 않는다. 필요한 발췌만 남긴다.

## structure

- [Owner Thought 변화 추적](./owner_thought_tracker.md)
- `notes/YYYY-MM-DD-<topic-slug>.md`

초기 backfill note:

- [2026-04-17-longitudinal-vs-transverse-weighting](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)
- [2026-04-17-dpf-as-progress-preference-device](./notes/2026-04-17-dpf-as-progress-preference-device.md)
- [2026-04-17-raw-thought-capture-workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)
