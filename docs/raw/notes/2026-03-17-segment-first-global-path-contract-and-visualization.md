# 전역 경로를 처음부터 세그먼트로 두는 계약과 시각화

## Date

- 2026-03-17

## Topic

- `segment-first global path contract and visualization`

## Source sessions

- confirmed materialized source: `$HOME/.codex/sessions/2026/03/18/rollout-2026-03-18T03-56-06-019cfd27-be1f-7671-a901-4be788cca7bd.jsonl`
- this note captures the user transition from behavior-side segment interpretation to a stronger global-planner segment contract

## User original messages

> 전역 경로를 생성할 때부터 하나가 아니라 세그먼트들로 만드는 방향? 어때? 그리고 그 인덱스와 노드를 소비하는 방식으로 그리고 노드랑 간선형태겠지? 계네도 rviz에서 시각화 하고 노드는 점 간선은 선 알겠지? 지금 그게 맞으면 원래 계획 실행하고

> 노드는 점이던 arrow던 상관 없어 볼 수만 있으면 그리고 arrow가 낫겠지

> PLEASE IMPLEMENT THIS PLAN:
> # Segment-First Global Path + Gate Consume + Lane-Bounded Local Splice
>
> ## Summary
> - global planner가 `planned_path_detailed.path_data.nodes + path_data.links`를 ordered segment sequence로 발행한다.
> - behavior planner는 `current_segment_index`와 `current_exit_node`를 소비한다.
> - RViz는 full graph와 selected segment path를 모두 표시한다.
> - 노드는 `ARROW`, 간선은 `LINE`으로 표시한다.

## Open questions at the time

- ordered segment contract를 메시지 의미로까지 고정할지
- full graph와 selected segment path를 어느 정도까지 같이 시각화할지
- node arrow/point choice가 설계 의미에 영향을 주는지, 아니면 purely visualization choice인지
