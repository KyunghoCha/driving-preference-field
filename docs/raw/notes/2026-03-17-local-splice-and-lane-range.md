# ego에서 다음 노드까지만 다시 만드는 splice와 차선 범위

## Date

- 2026-03-17

## Topic

- `local splice and lane range`

## Source sessions

- confirmed materialized source: `$HOME/.codex/sessions/2026/03/18/rollout-2026-03-18T03-56-06-019cfd27-be1f-7671-a901-4be788cca7bd.jsonl`
- this note captures the user transition from gate-only consume to `ego -> next` local splice bounded by lane range

## User original messages

> 잠시만 확실히 할게 더 있어 그니까 작은 글로벌 경로의 조각들로 하고 장애물때문에 지나갈때는 전체 경로를 다시 만드는게 아니라 ego에서 다음 노드까지만 경로를 다시 만드는 방향이 맞지? 그리고 범위는 차선범위로 새줘 규정에서 차선 범위로

> PLEASE IMPLEMENT THIS PLAN:
> # Segment-First Global Path + Gate Consume + Lane-Bounded Local Splice
>
> ## Summary
> - 장애물 때문에 현재 exit node로 바로 못 가면 전체 경로를 다시 만들지 않고 `ego -> current exit node`까지만 local splice를 만든다.
> - local splice는 규정 차선 안쪽 폭 기준 corridor 안에서만 `/costmap` 위 A*로 만든다.

## Open questions at the time

- lane range를 차선 폭 그대로 둘지, 차량 중심 corridor로 줄일지
- local splice가 실패했을 때 정지/대기와 재시도 경계를 어떻게 둘지
- local splice를 DPF progression의 본질로 볼지, blocked-case fallback으로만 볼지
