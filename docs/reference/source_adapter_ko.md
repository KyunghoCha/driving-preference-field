# Source Adapter

이 문서는 raw source를 canonical semantic contract로 번역하는 source adapter의 출력 계약을 정리한다. canonical로 고정하는 것은 raw source 형식이 아니라 `SemanticInputSnapshot + QueryContext`라는 output contract다.

## 책임

adapter는 의미 번역기만 한다.

- 담당:
  - raw source -> canonical `SemanticInputSnapshot + QueryContext`
- 비범위:
  - planner heuristic
  - branch winner 선택
  - 행동 계획
  - optimizer tuning
  - Gazebo / RViz / MPPI integration

## Canonical output

adapter output은 다음 두 타입으로 고정한다.

- `SemanticInputSnapshot`
- `QueryContext`

### SemanticInputSnapshot

공간 의미 자체를 담는다.

- 필수 slot:
  - `drivable_support`
  - `progression_support`
- optional slot:
  - `boundary_interior_support`
  - `branch_continuity_support`
  - `exception_layer_support`

추가 원칙:

- progression과 drivable은 분리된 semantic slot로 유지한다.
- branch winner는 canonical snapshot이 직접 정하지 않는다.
- support/confidence/branch prior 같은 값은 있더라도 weak prior metadata로만 다룬다.

### QueryContext

field를 어디서 어떻게 평가하는지를 담는다.

- 포함:
  - `ego_pose`
  - `local_window`
  - optional `mode`
  - optional `phase`

`ego_pose`는 snapshot 본체 의미가 아니라 질의 문맥(`QueryContext`) 책임이다. `local_window`의 크기와 slicing policy는 canonical truth가 아니라 experiment 영역으로 남긴다.

## Generic reference input schema

Phase 5 v1 reference adapter는 source-specific naming을 쓰지 않는 generic local semantic map fixture를 사용한다. reference schema는 아래 계층으로 구성한다.

- `metadata`
- `drivable_regions`
- `progression_supports`
- optional `progression_options`
- optional `boundaries`
- optional `boundary_regions`
- optional `branch_supports`
- optional `safety_regions`
- optional `rule_regions`
- optional `dynamic_regions`
- `query_context`

`query_context` 안에는 `query_pose` 또는 `ego_pose`, `local_window`, optional `mode`, optional `phase`가 들어간다.

## 필수와 optional

v1 reference adapter의 필수 입력은 다음이다.

- `drivable_regions`
- `progression_supports`
- `query_context`
  - `query_pose` 또는 `ego_pose`
  - `local_window`

optional 입력은 다음이다.

- `boundaries`
- `boundary_regions`
- `branch_supports`
- `safety_regions`
- `rule_regions`
- `dynamic_regions`
- guide/region metadata의 `support_confidence`, `branch_prior` 같은 weak prior

optional 항목이 없다고 canonical output이 invalid가 되지는 않는다.

## 보존해야 할 분리

adapter는 progression과 drivable을 하나로 합치지 않는다.

- `drivable_support`: 지금 local map에서 무엇이 움직일 수 있는 공간인가
- `progression_support`: 무엇이 앞이고 뒤인지, intended progression continuity를 어떤 흐름이 더 잘 지지하는가

branch winner는 canonical에서 정하지 않는다. 여러 candidate continuation을 continuity support로 전달할 수 있고, optional `branch_prior`가 있으면 weak prior metadata로만 전달한다. support/confidence도 본체가 아니라 optional weak prior다.

## 기존 toy path와의 관계

기존 `toy_loader` 경로는 유지한다.

- `toy_loader`: hand-authored toy case loader
- Phase 5 reference adapter: generic external-like semantic map -> canonical snapshot translator

평가기, raster, Parameter Lab, `FieldRuntime`는 adapter output이 같으면 그대로 재사용한다.

## Inspection path

현재 adapter inspection CLI는 다음을 지원한다.

- generic adapter input summary 출력
- canonical snapshot / query context bundle export
- validation failure 설명

목적은 integration 자체가 아니라, 실제 source를 canonical로 번역했을 때 의미가 맞는지 빠르게 확인하는 것이다.

## SSC와의 관계

SSC는 중요한 validation source지만 canonical 기준은 아니다.

- SSC naming을 reference schema에 넣지 않는다.
- SSC 자료구조를 canonical 타입에 직접 올리지 않는다.
- SSC에서 나온 요구사항은 evidence로만 사용한다.

## 현재 기준

source adapter의 canonical truth는 raw source가 아니라 `SemanticInputSnapshot + QueryContext` output contract이며, v1 reference adapter는 source-agnostic generic local semantic map fixture를 이 canonical contract로 번역하는 의미 번역기다.
