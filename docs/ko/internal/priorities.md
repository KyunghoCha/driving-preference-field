# 내부 우선순위

로드맵 phase 추적은 `docs/ko/status/roadmap.md`가 맡는다. 이 문서는 내부 작업 우선순위를 짧게 고정하는 메모다.

## P0: Phase 5 결과 안정화

- `Phase 5 완료, Phase 6 준비 상태` 문서, runtime contract, adapter contract, lab 동작을 계속 맞춘다.
- 입문 문서, status 문서, 현재 구현 메모 사이의 semantic drift를 막는다.
- 이 repo를 integration-specific branch가 아니라 score-field SSOT로 유지한다.

## P1: 반복 가능한 morphology 실험 유지

- Parameter Lab이 비교, export, profile inspection 실험에 계속 유용해야 한다.
- preset/config 비교를 기본 실험 단위로 유지한다.
- morphology retuning은 downstream evidence가 실제로 나올 때만 한다.

## P2: runtime query semantics 안정화

- `FieldRuntime` semantics를 evaluator semantics와 계속 맞춘다.
- downstream consumer가 formula copy가 아니라 runtime API를 쓰게 유지한다.
- cache와 debug tooling은 implementation detail로만 남긴다.

## P3: adapter contract를 generic하게 유지

- source adapter 가정은 source-agnostic하고 generic해야 한다.
- source-specific 구조를 canonical design docs나 contract type으로 올리지 않는다.
- SSC와 다른 downstream system은 validation source로만 다룬다.

## P4: planner, geometry editing, integration은 뒤로 미룬다

- planner / Gazebo / RViz / MPPI integration은 이 repo 범위 밖에 둔다.
- geometry editing은 현재 phase에서 다루지 않는다.
- interactive studio 같은 것은 cleaned-up lab 위의 다음 단계로 남긴다.
