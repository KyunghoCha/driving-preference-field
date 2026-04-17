# progress-first node progression과 frontier 우선 전진

## Date

- 2026-03-22

## Topic

- `progress-first node progression`
- `frontier-first blocked progression`

## Source sessions

- confirmed materialized source: `$HOME/.codex/sessions/2026/03/22/rollout-2026-03-22T13-18-10-019d13c3-c582-7811-9598-698f752a712a.jsonl`
- this note captures the point where gate/segment consume intuition is pressured by blocked progression and starts to split into progress-first and frontier-first blocked behavior

## User original messages

> 그냥 멈춰버리는데 아니면 장애물이 없다면 일단 진행은?

> 아니 행동이 경로를 못잡아주고 하니까 그런거 아니야

> 아니면 못가면 갈 수 있는곳까지 플래닝은?

> ㄴ내가 얘기하는거 좋다고만 하지 말고 좀 제대로 생각을 해보자 어떡하는게 좋을까

> 그렇게 해보자 구현 그거 하면 많이 더러워질까

> PLEASE IMPLEMENT THIS PLAN:
> # `SSC_test` Phase 4: Frontier-First Blocked Progression
>
> ## Summary
> `SSC_test`의 `behavior`만 수정한다. 목표는 “장애물 때문에 current/next node로 바로 못 갈 때, 노드를 억지로 consume하려 하지 말고 **갈 수 있는 frontier까지 local splice로 전진**”하도록 바꾸는 것이다.
>
> ## Key Changes
> - `planning_callback()`에서 blocked local splice 판단을 segment progression보다 먼저 수행한다.
> - `frontier` 또는 `obstacle` local splice가 active일 때는 normal outside-gate segment commit을 막는다.
> - “못 가면 일단 멈춤”이 아니라, **“못 가면 frontier까지, 그것도 안 되면 멈춤”**으로 정리한다.

## Open questions at the time

- gate consume와 blocked frontier 전진을 같은 progression 정의 안에 둘지
- frontier-first가 local splice fallback인지, 더 앞선 progression rule인지
- 이 전환을 이후 DPF progression semantics로 얼마나 직접 가져갈지
