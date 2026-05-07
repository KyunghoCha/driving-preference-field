# 세그먼트 인덱스 소비와 reachable progress

## Date

- 2026-03-17

## Topic

- `segment index consumption and reachable progress`

## Source sessions

- confirmed materialized source: `$HOME/.codex/sessions/2026/03/18/rollout-2026-03-18T03-56-06-019cfd27-be1f-7671-a901-4be788cca7bd.jsonl`
- this note captures the earlier user framing that appeared before the gate-only simplification and later LRPC design discussion

## User original messages

> 경로도 노드 사이를 글로벌에서 만들때 하나로 만드는게 아니라 노드 사이의 경로에 인덱스를 붙여서 소비하는 방식으로 하고 그리고 장애물때문데 당장 다음 노드로 못가도 계속 일단 갈 수 있는 길은 갈 수 있게 하는 방식으로 하고 동적 장애물로 앞에 갑자기 생기는 장애물도 있는데 그런건 어떻게 할까

> PLEASE IMPLEMENT THIS PLAN:
> # Segment-First Global Path + Gate Consume + Lane-Bounded Local Splice
>
> ## Summary
> 전역 경로를 “하나의 큰 path”가 아니라 `ordered node/edge segment path`로 만든다.
> - global planner가 `planned_path_detailed.path_data.nodes + path_data.links`를 ordered segment sequence로 발행한다.
> - behavior planner는 `current_segment_index`와 `current_exit_node`를 소비한다.

## Open questions at the time

- reachable progress를 gate consume과 어떤 관계로 둘지
- 동적 장애물이 있을 때 reachable frontier를 어떻게 해석할지
- segment consumption을 global planner contract까지 올릴지, behavior 내부 해석으로 둘지
