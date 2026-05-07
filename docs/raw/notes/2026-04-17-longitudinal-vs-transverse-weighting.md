# 진행방향 성분과 횡방향 성분 비중

## Date

- 2026-04-17

## Topic

- `longitudinal vs transverse weighting`

## Source sessions

- current active LRPC thread from the gate-intuition cluster onward; later portions of the thread were not yet materialized under `$HOME/.codex/sessions/...` at edit time
- early source anchor confirmed in `$HOME/.codex/sessions/2026/03/18/rollout-2026-03-18T03-56-06-019cfd27-be1f-7671-a901-4be788cca7bd.jsonl`

## User original messages

> 그리고 또 내가 생각해본게 진행방향 성분이 메인으로 가고 횡방향성분은 그렇게 강하지 않아도 될거 같아 그래야 지금 당장 손해를 보더라도 최적의 경로를 그릴 수 있을거 같거든 실제로 진행방향 성분이 실수로 좁아져서 많이 강해졌을때의 경로가 더 효율적이었으니까 아웃 인 아웃같은건 멀리 봐야하는 제약사항이 있겠지만 그런 생각이 들었어 경로 따라가는게 중요하면 횡방향성분을 강하게 하고 빨리 가는게 중요하면 진행방향 성분을 강하게 하고 그런식이 나는 괜찮을거 같다는 생각이 들었어 그리고 진행방향 성분이 생각보다 강해야 한다는 직관도 있고 지금은 정규화를 해서 그렇게 강해질 수가 없는 문제가 있는가? 그게 맞는지는 모르겠다 비율만 잘 조정하면 되는건지

> 1번은 파라미터로 조정하면 되는거고 필요에 맞게 그렇게 만들어야지 아니야? 그럼 행동계획이나 걔들이 책임 지겠지 우리는 그걸 책임지면 안되는거야

> 2변은 진행 선호를 주는 장치지 경로를 붙잡는다는게 글로벌인지 로컬인지 모르겠는데 애초에 입력에 경로가 부분이긴 하지만 결국 어디로 가는게 좋냐는거잖아

## Assistant context (optional)

- 대화에서 분리된 구분: `Normalized` scale은 visualization range를 다시 잡는 것이지, 계산된 score에서 `longitudinal` dominance 자체를 막는 것은 아니라는 설명이 있었다.
- 현재 score 구조상 `transverse + gain * longitudinal` 형태의 trade-off가 이미 존재한다는 점이 맥락으로 확인됐다.

## Open questions at the time

- 이 문제는 tuning인가, LRPC object definition인가
- longitudinal dominance를 높여도 branch/corridor structure를 어디까지 유지해야 하는가
- `Fixed` scale 기준으로도 같은 직관이 유지되는가
