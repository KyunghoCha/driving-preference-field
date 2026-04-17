# 시뮬 비교 방법론과 MPPI 최적화 실험 분리

## Date

- 2026-04-18

## Topic

- `simulator comparison methodology`
- `real-time constrained benchmark vs fixed-budget benchmark`
- `MPPI tuning / Pareto frontier`

## Source sessions

- current active SSC/DPF comparison discussion thread on 2026-04-18
- current thread was explicitly treated as the authoritative source for this design direction

## User original messages

> 실험에 파라미터 수정도 있어? mppi를 얼마나 최적화 할 수 있는지 그런거도 하고싶거든

> 그렇긴 한데 너가 hz를 못올린다면서 그럼 원래 mppi를 낮춰야 하나 아니면 해결하면 되나 낮추면 제대로된 실험이 아닐거 같아서

> 해봐

## Assistant context (optional)

- 대화에서는 `DPF-current-port`를 실험 본체에서 빼고 `SSC-baseline` vs 미래 `DPF-next` 비교로 다시 정리하는 흐름이 먼저 합의됐다.
- 이어서 사용자는 성능 비교만이 아니라 `mppi를 얼마나 최적화할 수 있는지`, 그리고 `Hz를 못 올릴 때 실험을 어떻게 공정하게 설계해야 하는지`를 함께 보고 싶다고 명시했다.
- 이 지점에서 assistant는 세 가지 실험을 분리해야 한다고 정리했다.
  - `real-time constrained benchmark`: target Hz를 고정하고, 그 제약을 만족하도록 내부 MPPI budget을 조정한 상태에서 baseline과 DPF를 비교
  - `fixed-MPPI-budget benchmark`: `batch_size`, `time_steps`, `model_dt` 같은 planning budget을 고정하고, achieved Hz와 overrun이 얼마나 달라지는지 측정
  - `parameter optimization / Pareto tuning study`: MPPI budget과 behavior 파라미터를 sweep해서 성능 대 비용 frontier를 그림
- 사용자의 핵심 우려는 `DPF가 느리다고 그냥 Hz를 낮춰서 비교하면 제대로 된 실험이 아닌 것 같다`는 점이었다.
- 따라서 메인 비교는 외부 real-time 제약을 고정하고, 별도 실험에서 fixed-budget cost와 tuning 가능성을 따로 보는 방향이 current thread에서 잠겼다.

## Locked design transition in this thread

- 메인 benchmark는 `같은 real-time target 안에서 누가 더 잘 가는가`를 본다.
- 별도 benchmark는 `같은 MPPI budget에서 누가 더 무거운가`를 본다.
- 또 별도 tuning study는 `어디까지 줄여도 성능이 유지되는가`와 `어디서부터 비용 대비 성능이 꺾이는가`를 본다.
- 즉 공정 비교, 구조 비용 비교, tuning frontier를 하나의 표로 섞지 않고 분리해서 기록한다.

## Open questions at the time

- tuned common target profile을 어느 숫자로 잠글지
- tuning set과 held-out evaluation set을 scenario 차원에서 어떻게 나눌지
- CPU/GPU usage를 어떤 수집 방식으로 표준화할지
