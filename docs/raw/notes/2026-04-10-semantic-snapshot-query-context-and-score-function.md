# Semantic Snapshot, Query Context, 그리고 score function 언어

## Date

- 2026-04-10

## Topic

- `semantic snapshot`
- `query context`
- `score function framing`

## Source sessions

- confirmed materialized source: `$HOME/.codex/sessions/2026/04/10/rollout-2026-04-10T20-19-15-019d771e-1c0e-7d13-a07f-2a739347cd9c.jsonl`
- this note captures the user's raw clarification of what should stay canonical, what should remain experimental, and how the work might be named in later writing

## User original messages

> 1. 의미번역기만 2. 주행가능영역인데 주행가능영역의 중앙을 기준으로 분포만 잘 만들면 될듯 튜브처럼 주행가능영역을 뽑기보다는 다른 필수는 있으면 좋겠지 왜냐면 가제보에서 해보니까 로컬에서 바로 주행가능 영역을 뽑는거도 되긴 하는데 글로벌노드나 그런걸 기준으로 뽑고 주행가능 영역은 나중에 알아서 뽑고 글로벌의 점수장을 따라 그 주행가능영역을 움직이는데 주행가능영역이 글로벌을 좀 벗어나거나 해도 주행의 의미는 사라지지 않는 그런걸 원했었어 나머지 progression_guides ego_pose local_window나 다른것들은 좀 더 알아봐야 될거 같은데 이 의미데서 egp_pose는 최소 필수 출력이 아니지 않나 점수장을 만드는데 사용되지 않는다고 생각해 ego가 거기 영향을 주면 원래 주행 의도랑 달라질 수 있다는 생각도 들어서 3. local map의 범위는 지금 가제보에서 해보고 있는데 차마다 달라지고 아니면 동적으로 해야될 수도 있겠다는 생각이 들더라고 너무 크면 u턴에서 그 다음 노드의 점수까지 다 나와서 의도랑 다르게 움직이고 뭐 이거도 차선이 없었어서 당연한 결과지만 범위를 잘 정해야 의도를 잘 반영하겠더라고 이건 실험영역으로 남겨둬야 할거 같아 4. progression은 내가 뭔지 정확하게 이해를 못해서 설명해줘 5. branch는 전역경로에서 A*나 그런거로 가중치가 높게 나오는 그런게 있다면 그 가중치를 반영해서 점수를 어떻게 해도 좋을거 같고 아니면 너가 얘기한데로 기본은 winner을 정하지는 않고 행동계획이나 그런데 맞기는거지 그게 맞는거 같아 앞에서 얘기한거보다 왜냐면 우리는 공간을 알려주지 방향을 알려주는건 아니잖아 6. 이거도 이해를 못해서 설명해줘 7. 넣지 말아야할것들 너가 얘기한거도 좋은데 맞지 그게 나는 범용성을 생각하고 있어서 8. SSC는 우리가 만든거의 실제 적용해본다에 의의지 완전 하위의 어떤거야 SSC는 SSC하다가 이 아이디어를 얻은거긴 하지만 그래서 내가 만든 점수장이 범용성이 있을지는 알아봐야겠지만 SSC에 매몰되면 절대 안되 9. 구현 순서는 너가 알아서 해 10. 이거도 너가 알아서 이정도? 대화를 더 하자

> 6번도 실험 영역인거 같고 진행 하는데 우선 내 생각을 잘 알겠어?

> 문서들 전부 최신화 하고 누가 처음봐도 내 생각을 알 수 있을 정도로 그리고 진행하자

> - **Semantic Input Snapshot**: local map의 의미 정보
> - **Query Context**: 평가 시점의 문맥 정보
> 얘네를 각각 어떤 의민지 표로 만들어주고 설명도

> 선배가 이해하셨어 스코어 펑션쪽으로 잡아서 써보라고 하셨는데 어떻게 생각해?

> [차경호] [11:54 PM] 이제 올라와서 쓰려고 하는데 선배가 얘기하신게 score function 맞나요? Wednesday, April 15, 2026 [배경민] [1:47 AM] 그것도 비슷한 단어긴 한데 [배경민] [1:47 AM] Cost func에서 특히 goal cost func을 말하긴했음 선배가 이걸 그 뭐라하더라 이 바운더리? 로 논문 개조식 초안 작성해보라고 하시더라고 어떻게 생각해? 지금까지 정리한거는 그냥 노션 정리한거고 개조식은 다른거야

> 아니 goal cost func분야라고 그런게 아니라 내가 하고싶었단 말은 분야도 정확한 단언지는 모르겠는데 저 세션? 뭐라하지 ㅋㅋ 쨌든 goal cont func로 작성해보라고 하셨어

> 근데 그럼 내가 생각한거랑은 조금 달라지지 않아? 아닌가?

> 선호장이랑 저거중에 너는 뭐가 더 낫다고 봐? 그리고 goal cost func를 양수로 쓸 수는 없는거야?

## Open questions at the time

- `Semantic Input Snapshot`와 `Query Context` 경계를 canonical로 얼마나 단단히 잠글지
- `ego_pose`, `local_window`, branch winner 같은 항목을 canonical이 아닌 experiment 영역으로 계속 둘지
- `선호장`, `score function`, `goal cost function` 중 어떤 언어가 사용자 의도와 가장 덜 어긋나는지
