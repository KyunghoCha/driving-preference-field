# DPF를 진행 선호 장치로 보는 생각

## Date

- 2026-04-17

## Topic

- `DPF as progress-preference device`

## Source sessions

- current active Codex session on 2026-04-17 in VSCode; the active session was not yet materialized under `$HOME/.codex/sessions/...` at edit time
- local recording surfaces confirmed during backfill: `$HOME/.codex/history.jsonl`, `$HOME/.codex/session_index.jsonl`, `$HOME/.codex/sessions/...`, `$HOME/.codex/archived_sessions/...`

## User original messages

> 1번은 파라미터로 조정하면 되는거고 필요에 맞게 그렇게 만들어야지 아니야? 그럼 행동계획이나 걔들이 책임 지겠지 우리는 그걸 책임지면 안되는거야

> 그래서 내가 한 대화들을 넣으라는거지 내가 채팅에 친것들을 너의 답변도 필요하면 명시해서 넣는거고 그리고 대화 다 기록에 남는게 있다고 채팅이 그래서 그걸 보고 하라고 한거고 확인을 하라고 한거야 안그러면 지금 vscode에서 어떻게 띄우는데 그리고 corridor fidelity vs optimizer-upstream preference 이쪽일까 영어라서 확실하지는 않은데 후진을 하면 진행방향 성분만 위로 기울게 하면 되는거라 그런식으로 생각을 했거든 좀 더 대화를 하고 그 다음 진행을 하는게 좋을듯

> 2변은 진행 선호를 주는 장치지 경로를 붙잡는다는게 글로벌인지 로컬인지 모르겠는데 애초에 입력에 경로가 부분이긴 하지만 결국 어디로 가는게 좋냐는거잖아

## Assistant context (optional)

- 대화 중 assistant가 사용한 영어 표현 `corridor fidelity vs optimizer-upstream preference`는 당시 비교용 구분이었고, 사용자 쪽에서는 “진행 선호를 주는 장치”라는 한국어 framing이 더 정확하다고 명시됐다.
- 대화 맥락에서 `경로를 붙잡는다`는 말은 global route가 아니라 local corridor/centerline 유지 쪽을 가리키는 것으로 구분됐다.

## Open questions at the time

- DPF가 downstream planner보다 path responsibility를 얼마나 적게 져야 하는가
- 입력 경로를 reference로만 쓸지, stronger corridor prior로도 볼지
- 후진/반대 진행 bias도 같은 longitudinal framing으로 설명할지
