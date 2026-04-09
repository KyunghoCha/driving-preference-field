# SSC 입력 매핑 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 SSC가 현재 `driving-preference-field`에 제공할 수 있는 입력을 reading 관점에서 정리한다.

이 문서는 canonical 정의 문서가 아니다. 현재 SSC가 어떤 종류의 입력을 제공하는지와, 어떤 부분이 추가 adapter를 필요로 하는지를 참고용으로만 정리한다.

## Canonical Slot 기준 매핑

| SSC raw source | 대응 가능한 canonical slot | 현재 수준 |
| --- | --- | --- |
| waypoint / ordered path / goal sequence | progression support | 바로 활용 가능 |
| graph / route continuity 정보 | progression support, branch / continuity support | adapter 필요 |
| local costmap obstacle / inflation | exception-layer support, 일부 boundary support | 바로 활용 가능 |
| lane layer / lane pointcloud | drivable support, boundary / interior support | adapter 필요 |
| local free-space shape | drivable support, boundary / interior support | adapter 필요 |

## 바로 활용 가능한 입력

### 1. 진행 의미 관련 입력

SSC는 현재 다음과 같은 progression semantics를 이미 가지고 있다.

- ordered waypoint / segment sequence
- current goal과 next waypoint sequence
- reverse 관련 flag
- path index / node type

즉 진행 순서, 진행 방향, local continuity를 읽어낼 수 있는 기초 정보는 이미 존재한다.

### 2. safety / obstacle 관련 입력

SSC는 현재 다음과 같은 safety semantics를 이미 가지고 있다.

- local costmap
- obstacle layer
- inflation 성격의 cost band

즉 obstacle / safety 계층의 입력은 별도 layer로 연결하기 충분한 수준이다.

### 3. lane / drivable 관련 입력

SSC는 현재 다음과 같은 local drivable 의미를 부분적으로 제공한다.

- lane mask
- lane pointcloud
- costmap 내부 lane layer

즉 local drivable structure의 흔적은 이미 올라오고 있다.

## adapter가 필요한 입력

다음은 현재 raw source만으로는 바로 canonical input으로 보기 어렵고, adapter 정리가 필요한 항목이다.

- drivable patch의 interior / boundary structure 정리
- branch continuity를 field generator 입력으로 정리
- waypoint / path 의미를 progression semantics contract로 정리
- local lane 흔적을 field 입력용 geometry/semantics로 재구성

즉 SSC는 재료는 제공하지만, field generator가 직접 소비할 입력 계약은 아직 별도로 정리해야 한다.

## 아직 약한 부분

현재 SSC에서 약한 것은 다음과 같다.

- 풍부한 branch preference semantics
- interior structure의 graded interpretation
- field generator 전용 canonical input contract

즉 SSC는 prototype input source로는 충분히 유용하지만, 최종 canonical 입력 구조를 그대로 대체하지는 않는다.

## 현재 기준 결론

한 줄로 요약하면:

SSC는 `주행 가능 의미 + 진행 의미 + safety 관련 입력`의 실제 source로 사용할 수 있지만, field generator가 직접 소비할 수준의 입력 계약은 별도 adapter를 통해 정리해야 한다.
