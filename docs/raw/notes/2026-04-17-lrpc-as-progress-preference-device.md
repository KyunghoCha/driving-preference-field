# LRPC를 진행 선호 장치로 보는 생각

## Date

- 2026-04-17

## Topic

- `LRPC as progress-preference device`

## Source sessions

- current active LRPC thread from the gate-intuition cluster onward; later portions of the thread were not yet materialized under `$HOME/.codex/sessions/...` at edit time
- early source anchor confirmed in `$HOME/.codex/sessions/2026/03/18/rollout-2026-03-18T03-56-06-019cfd27-be1f-7671-a901-4be788cca7bd.jsonl`

## User original messages

> 그리고 또 내가 생각해본게 진행방향 성분이 메인으로 가고 횡방향성분은 그렇게 강하지 않아도 될거 같아 그래야 지금 당장 손해를 보더라도 최적의 경로를 그릴 수 있을거 같거든 실제로 진행방향 성분이 실수로 좁아져서 많이 강해졌을때의 경로가 더 효율적이었으니까 아웃 인 아웃같은건 멀리 봐야하는 제약사항이 있겠지만 그런 생각이 들었어 경로 따라가는게 중요하면 횡방향성분을 강하게 하고 빨리 가는게 중요하면 진행방향 성분을 강하게 하고 그런식이 나는 괜찮을거 같다는 생각이 들었어 그리고 진행방향 성분이 생각보다 강해야 한다는 직관도 있고 지금은 정규화를 해서 그렇게 강해질 수가 없는 문제가 있는가? 그게 맞는지는 모르겠다 비율만 잘 조정하면 되는건지

> 1번은 파라미터로 조정하면 되는거고 필요에 맞게 그렇게 만들어야지 아니야? 그럼 행동계획이나 걔들이 책임 지겠지 우리는 그걸 책임지면 안되는거야

> 그래서 내가 한 대화들을 넣으라는거지 내가 채팅에 친것들을 너의 답변도 필요하면 명시해서 넣는거고 그리고 대화 다 기록에 남는게 있다고 채팅이 그래서 그걸 보고 하라고 한거고 확인을 하라고 한거야 안그러면 지금 vscode에서 어떻게 띄우는데 그리고 corridor fidelity vs optimizer-upstream preference 이쪽일까 영어라서 확실하지는 않은데 후진을 하면 진행방향 성분만 위로 기울게 하면 되는거라 그런식으로 생각을 했거든 좀 더 대화를 하고 그 다음 진행을 하는게 좋을듯

> 2변은 진행 선호를 주는 장치지 경로를 붙잡는다는게 글로벌인지 로컬인지 모르겠는데 애초에 입력에 경로가 부분이긴 하지만 결국 어디로 가는게 좋냐는거잖아

## Assistant context (optional)

- 대화 중 assistant가 사용한 영어 표현 `corridor fidelity vs optimizer-upstream preference`는 당시 비교용 구분이었고, 사용자 쪽에서는 “진행 선호를 주는 장치”라는 한국어 framing이 더 정확하다고 명시됐다.
- 대화 맥락에서 `경로를 붙잡는다`는 말은 global route가 아니라 local corridor/centerline 유지 쪽을 가리키는 것으로 구분됐다.
- 위의 `1번` / `2변` 표현은 당시 assistant가 번호를 붙여 정리한 응답과 직후 대화를 가리킨다. 이 note에서는 해당 표현이 끊기지 않도록 앞뒤 사용자 메시지를 함께 남긴다.

## Open questions at the time

- LRPC가 downstream planner보다 path responsibility를 얼마나 적게 져야 하는가
- 입력 경로를 reference로만 쓸지, stronger corridor prior로도 볼지
- 후진/반대 진행 bias도 같은 longitudinal framing으로 설명할지
