# 소스 어댑터

이 문서는 raw source를 canonical semantic contract로 번역하는 source adapter의 출력 계약을 정리한다. canonical로 고정하는 것은 raw source 형식이 아니라 `SemanticInputSnapshot + QueryContext`라는 output contract다. 이 문서는 adapter가 무엇을 출력해야 하는지, 어떤 slot이 필수이고 어떤 slot이 optional인지, 그리고 무엇을 canonical로 올리지 않는지 찾아보기 중심으로 정리하는 reference다.

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

## 출력 계약

adapter output은 다음 두 타입으로 고정한다.

- `SemanticInputSnapshot`
- `QueryContext`

### SemanticInputSnapshot

공간 의미 자체를 담는다.

- 필수 slot:
  - `progression_support`
  - `drivable_support`
- optional slot:
  - `boundary_interior_support`
  - `exception_layer_support`

추가 원칙:

- `progression_support`는 base preference를 만드는 본체 support다.
- `drivable_support`는 domain / support / reconstruction 재료다.
- progression과 drivable은 분리된 semantic slot로 유지한다.
- branch winner는 canonical snapshot이 직접 정하지 않는다.
- support/confidence 같은 값은 있더라도 weak prior metadata로만 다룬다.

`boundary_interior_support`는 optional geometry prior다. split/merge continuity는 별도 slot보다 multiple progression guide 표현으로 다루며, canonical base를 항상 구성하는 필수 slot로 materialize하지 않는다.

### QueryContext

field를 어디서 어떻게 평가하는지를 담는다.

- 포함:
  - `ego_pose`
  - `local_window`
  - optional `mode`
  - optional `phase`

`ego_pose`는 snapshot 본체 의미가 아니라 질의 문맥(`QueryContext`) 책임이다. `local_window`의 크기와 slicing policy는 canonical truth가 아니라 experiment 영역으로 남긴다.

`QueryContext`는 field 의미 자체를 바꾸는 입력이 아니라, 같은 semantic snapshot을 어디서 어떻게 평가할지를 정하는 evaluation context다.

## `generic reference` 입력 스키마

Phase 5 v1 reference adapter는 source-specific naming을 쓰지 않는 generic local semantic map fixture를 사용한다. reference schema는 아래 계층으로 구성한다.

- `metadata`
- `drivable_regions`
- `progression_supports`
- optional `progression_options`
- optional `boundaries`
- optional `boundary_regions`
- optional `safety_regions`
- optional `rule_regions`
- optional `dynamic_regions`
- `query_context`

`query_context` 안에는 `query_pose` 또는 `ego_pose`, `local_window`, optional `mode`, optional `phase`가 들어간다.

## 필수와 optional

v1 reference adapter의 최소 raw 입력은 다음이다.

- `drivable_regions`
- `query_context`
  - `query_pose` 또는 `ego_pose`
  - `local_window`

progression 입력은 아래 우선순위로 받는다.

1. `progression_supports`
2. `global_plan_supports`
3. `drivable_regions`로부터의 bounded reconstruction

optional 입력은 다음이다.

- `boundaries`
- `boundary_regions`
- `safety_regions`
- `rule_regions`
- `dynamic_regions`
- guide/region metadata의 `support_confidence` 같은 weak prior

optional 항목이 없다고 canonical output이 invalid가 되지는 않는다.

## 보존해야 할 분리

adapter는 progression과 drivable을 하나로 합치지 않는다.

- `progression_support`: 무엇이 앞이고 뒤인지, intended progression continuity를 어떤 흐름이 더 잘 지지하는가
- `drivable_support`: 지금 local map에서 무엇이 움직일 수 있는 공간인가, 그리고 progression support를 어떻게 지지하거나 복원할 수 있는가

branch winner는 canonical에서 정하지 않는다. split/merge는 shared prefix/suffix를 가진 multiple progression guide로 전달하고, support/confidence는 본체가 아니라 optional weak prior다.

## 기존 toy path와의 관계

기존 `toy_loader` 경로는 유지한다.

- `toy_loader`: hand-authored toy case loader
- Phase 5 reference adapter: generic external-like semantic map -> canonical snapshot translator

평가기, raster, Parameter Lab, `FieldRuntime`는 adapter output이 같으면 그대로 재사용한다.

## 점검 경로

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

즉 adapter는 SSC를 포함한 어떤 source라도 같은 output contract로 번역해야 한다. source-specific 구조를 canonical로 승격하지 않는다는 경계가 이 문서의 핵심이다.

## 현재 구현

Phase 5 v1 reference adapter는 generic local semantic map fixture를 `SemanticInputSnapshot + QueryContext`로 번역한다. 현재 runtime과 toy path는 같은 output contract를 공유한다. raw adapter boundary에서는 progression 입력을 explicit guide, global plan, drivable-only reconstruction 중 하나로 받을 수 있다.

현재 normalization 정책은 source kind마다 다르게 둔다.

- `global_plan_supports`와 drivable-only reconstruction은 adapter의 정상 입력이므로, obvious single-chain fragmentation은 canonical guide 하나로 정규화할 수 있다.
- explicit `progression_supports`는 여전히 upstream 책임으로 문서화하지만, obvious single-chain fragmentation에 대해서는 adapter가 best-effort fallback normalization을 시도하고 그 사실을 snapshot metadata에 남긴다.
- split/merge처럼 ambiguous한 continuation은 조용히 추측하지 않는다. 이 경우 입력을 병합하지 않고 warning/error 수준의 normalization metadata만 남긴다.

## 현재 기준

source adapter의 canonical truth는 raw source가 아니라 `SemanticInputSnapshot + QueryContext` output contract이며, v1 reference adapter는 source-agnostic generic local semantic map fixture를 이 canonical contract로 번역하는 의미 번역기다.
