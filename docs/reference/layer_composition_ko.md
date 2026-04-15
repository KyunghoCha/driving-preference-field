# Layer 조합

- 역할: reference
- 현재성: canonical
- 대상 독자: contributor
- 다음으로 읽을 문서: [06. Runtime Contract](./runtime_evaluation_contract_ko.md)

작성일: 2026-04-08

## 문서 목적

이 문서는 base driving preference field와 예외 레이어를 왜 분리해야 하는지, 그리고 prototype 단계에서 어떤 조합 규칙을 따라야 하는지 정리한다.

## 기본 원칙

이 프로젝트는 다음을 같은 층으로 보지 않는다.

- base driving preference field
- safety / obstacle layer
- rule layer
- dynamic interaction layer

## 왜 단순 가산이 canonical이 아닌가

단순히 다 더하면 다음 문제가 생길 수 있다.

- 상쇄되면 안 되는 의미가 상쇄된다
- ideal driving preference가 안전 penalty에 묻혀 사라진다
- 어떤 제약은 soft preference가 아니라 composition rule이어야 한다

따라서 단순 가산은 canonical 조합 규칙이 아니다.

## 레이어별 조합 규칙

| Layer | 역할 | Soft additive | Gating / Masking | Constraint-like | 상쇄 금지 의미 |
| --- | --- | --- | --- | --- | --- |
| Base field | ideal driving preference 생성 | base field 내부 항 사이에서는 가능 | 기본 아님 | 기본 아님 | 다른 레이어가 base field의 의미를 “좋은 상태”로 재해석하면 안 됨 |
| Safety / Obstacle | 충돌, clearance, 비주행 영역 관계 | clearance 같은 soft term은 가능 | occupied / blocked 상태에는 적합 | 충돌 상태에는 필요 | hard unsafe 상태는 base preference로 상쇄되면 안 됨 |
| Rule | legal / operational restriction | 위반 정도가 연속적일 때만 일부 가능 | 금지 영역, hard rule 위반에는 적합 | hard rule에는 필요 | hard rule violation은 base preference로 상쇄되면 안 됨 |
| Dynamic Interaction | 다른 actor와의 관계 | courtesy / soft interaction에는 가능 | predicted collision에는 적합 | collision-risk에는 필요 | 충돌 위험은 base preference로 상쇄되면 안 됨 |

## Prototype 기본 조합 순서

현재 문서 라운드에서 prototype-friendly 기본 조합 순서는 다음으로 둔다.

1. hard violation flag를 먼저 판정한다
2. hard violation이 없으면 soft exception burden을 계산한다
3. 같은 hard/soft 조건 안에서 base field preference를 비교한다

즉 prototype에서는 단일 스칼라 합보다, layer-wise output과 ordering rule을 먼저 canonical로 둔다.

## 이 문서가 아직 고정하지 않는 것

현재는 다음을 아직 최종 고정하지 않는다.

- max-like composition
- gating
- masking
- lexicographic rule
- constrained optimization coupling

중요한 것은 “단순 합이 canonical이 아니다”, “레이어마다 허용되는 조합 방식이 다르다”, 그리고 “prototype 기본 순서는 hard -> soft -> base”라는 점을 먼저 고정하는 것이다.

## 현재 기준 결론

이 프로젝트에서 layer는 보기 좋게 여러 장으로 나누는 시각화가 아니라, **의미가 다른 층을 상쇄 없이 유지하고 비교 순서를 보존하기 위한 구조**다.
