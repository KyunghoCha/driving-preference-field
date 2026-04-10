# Source Adapter 설계 문서

작성일: 2026-04-10

## 문서 목적

이 문서는 raw source를 canonical semantic contract로 번역하는 **Phase 5 source adapter SSOT**를 고정한다.

이 문서의 핵심은 다음이다.

- canonical truth는 raw source가 아니라 **adapter output contract**다
- adapter는 의미 번역기만 한다
- source-specific 자료구조 이름은 canonical 안으로 새지 않는다

## 핵심 원칙

### 1. adapter는 의미 번역기만 한다

adapter는 raw source를 canonical semantic slot으로 번역한다.

즉:

- raw source -> canonical `SemanticInputSnapshot + QueryContext`

까지만 담당한다.

다음은 adapter 책임이 아니다.

- planner heuristic
- branch winner 선택
- 행동 계획
- optimizer tuning
- Gazebo / RViz / MPPI integration

### 2. raw source가 아니라 output contract가 canonical이다

이 프로젝트는 특정 외부 시스템의 wire format을 canonical truth로 올리지 않는다.

canonical로 고정하는 것은 다음이다.

- 어떤 semantic slot이 있어야 하는가
- 어떤 slot이 필수이고 optional인가
- 어떤 정보가 snapshot에 속하고, 어떤 정보가 query context에 속하는가

## Canonical Adapter Output

adapter output은 계속 다음 두 타입으로 고정한다.

- `SemanticInputSnapshot`
- `QueryContext`

### SemanticInputSnapshot

snapshot은 **공간 의미 자체**를 담는다.

v1에서 필수로 채우는 slot:

- `drivable_support`
- `progression_support`

v1에서 optional로 채울 수 있는 slot:

- `boundary_interior_support`
- `branch_continuity_support`
- `exception_layer_support`

여기서 중요한 점은 다음이다.

- progression과 drivable은 분리된 semantic slot로 유지한다
- branch winner는 canonical snapshot이 직접 정하지 않는다
- support/confidence/branch prior 같은 값은 있어도 **weak prior metadata**로만 다룬다

### QueryContext

query context는 **field를 어디서 어떻게 평가하는지**를 담는다.

포함되는 것:

- `ego_pose`
- `local_window`
- optional `mode`
- optional `phase`

즉 `ego_pose`는 snapshot 본체 의미가 아니라 QueryContext 책임이다.

또한 `local_window` 크기와 slicing policy는 canonical truth가 아니라 **experiment 영역**으로 남긴다.

## Generic Reference Input Schema

Phase 5 v1 reference adapter는 source-specific naming을 쓰지 않는 **generic local semantic map fixture**를 사용한다.

reference schema는 다음 계층으로 구성한다.

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

`query_context` 안에는 다음이 들어간다.

- `query_pose` 또는 `ego_pose`
- `local_window`
- optional `mode`
- optional `phase`

이 schema는 reference adapter용 입력일 뿐, canonical truth는 여전히 **output contract**다.

## 필수와 Optional

v1 reference adapter의 필수 입력은 다음으로 고정한다.

- `drivable_regions`
- `progression_supports`
- `query_context`
  - `query_pose` 또는 `ego_pose`
  - `local_window`

optional 입력은 다음으로 둔다.

- `boundaries`
- `boundary_regions`
- `branch_supports`
- `safety_regions`
- `rule_regions`
- `dynamic_regions`
- guide/region metadata의 `support_confidence`, `branch_prior` 같은 weak prior

optional 항목이 없다고 canonical output이 invalid가 되지는 않는다.

## progression과 drivable의 역할

adapter는 progression과 drivable을 하나로 합치지 않는다.

- `drivable_support`:
  - 지금 local map에서 무엇이 움직일 수 있는 공간인가
- `progression_support`:
  - 이 local place에서 무엇이 앞이고 뒤인가
  - intended progression continuity를 어떤 흐름이 더 잘 지지하는가

즉 canonical input은 “주행 가능 의미 + 진행 의미”를 분리해서 field generator에 전달한다.

## branch, support, confidence

branch는 canonical에서 winner를 정하지 않는다.

가능한 역할은 다음과 같다.

- 여러 candidate continuation을 branch continuity support로 전달
- optional `branch_prior`가 있으면 weak prior metadata로만 전달

support/confidence도 본체가 아니라 optional weak prior다.

즉:

- source 품질이 낮거나 ambiguity가 있을 때 과확신을 줄이는 데 쓸 수는 있다
- field 본체 의미를 새로 정의하는 slot로 승격하지는 않는다

exact transport shape와 weighting semantics는 여전히 experiment 영역이다.

## Toy Loader와의 관계

기존 `toy_loader` 경로는 유지한다.

- `toy_loader`:
  - hand-authored toy case loader
- Phase 5 reference adapter:
  - generic external-like semantic map -> canonical snapshot translator

둘은 병행 유지한다.

평가기, raster, Parameter Lab, `FieldRuntime`는 **adapter output이 같으면 그대로 재사용**한다.

## CLI / Inspection Path

Phase 5 v1은 adapter inspection용 CLI를 제공한다.

- generic adapter input summary 출력
- canonical snapshot / query context bundle export
- validation failure 설명

이 CLI의 목적은 integration이 아니라, **실제 source를 canonical로 번역했을 때 의미가 맞는지 빠르게 확인하는 것**이다.

## SSC와의 관계

SSC는 중요한 validation source지만 canonical 기준이 아니다.

이 문서의 원칙:

- SSC naming을 reference schema에 넣지 않는다
- SSC 자료구조를 canonical 타입에 직접 올리지 않는다
- SSC에서 나온 요구사항은 evidence로만 사용한다

즉 SSC는 downstream validation source고, 이 repo는 adapter SSOT를 유지한다.

## 현재 기준 결론

한 줄로 요약하면:

Phase 5 source adapter의 canonical truth는 raw source가 아니라 **`SemanticInputSnapshot + QueryContext` output contract**이며, v1 reference adapter는 source-agnostic generic local semantic map fixture를 이 canonical contract로 번역하는 의미 번역기다.
