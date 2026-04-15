# 00. 프로젝트 개요

- 역할: explanation
- 현재성: canonical
- 대상 독자: newcomer
- 다음으로 읽을 문서: [01. 운영 원칙](./engineering_operating_principles_ko.md)

작성일: 2026-04-10

## 문서 목적

이 문서는 `driving-preference-field`를 처음 보는 사람이 프로젝트의 핵심 생각과 현재 위치를 가장 빠르게 이해하도록 돕는 newcomer용 canonical overview다.

이 문서는 구현 디테일이나 history를 길게 설명하지 않는다. 대신 이 프로젝트가 무엇을 하려는지, 왜 이런 field가 필요한지, 무엇을 canonical truth로 보고 무엇을 아직 열어두는지를 직접 설명한다.

## 이 프로젝트가 왜 필요한가

이 프로젝트의 출발점은 다음 문제의식이다.

- ideal driving preference를 한 줄의 reference path 추종만으로는 충분히 표현하기 어렵다
- 지금 당장 가장 가까운 중심이나 가장 직접적인 선택이 항상 좋은 trajectory를 만들지는 않는다
- obstacle, rule, dynamic actor 같은 현실 예외와, ideal driving preference 자체는 같은 층이 아니다
- planner나 optimizer가 자연스럽게 trajectory를 만들게 하려면, discrete route보다 먼저 **공간 전체의 선호 구조**가 필요하다

즉 이 프로젝트는 “어떤 한 경로를 따라가라”를 먼저 정의하는 쪽보다, **지금 보이는 local map 전체에서 어디가 더 바람직한가**를 먼저 정의하는 쪽을 택한다.

## 이 프로젝트가 만드는 것

이 프로젝트의 본체는 `base driving preference field`다.

이 field는:

- source-agnostic semantic input을 받아
- 현재 보이는 local map 전체를 평가하고
- 어떤 상태와 trajectory가 더 바람직한지를 ordering으로 만들어 주는
  preference structure다

즉 canonical 중심은 “path scorer”가 아니라 **whole-space preference field**다.

## progression과 drivable을 왜 분리해서 보는가

이 프로젝트는 local drivable region만으로는 주행 의미를 충분히 표현할 수 없다고 본다.

이유는 다음과 같다.

- local drivable region은 지금 움직일 수 있는 공간을 알려주지만, 무엇이 앞이고 뒤인지 자체를 충분히 보존하지 못할 수 있다
- 반대로 progression 의미는 장기적인 진행 ordering을 주지만, 실제로 지금 어디를 움직일 수 있는지까지 말해주지는 않는다

그래서 canonical 관점에서는 최소한 다음을 분리해서 본다.

- **drivable semantics**: 지금 local map에서 무엇이 움직일 수 있는 공간인가
- **progression semantics**: 이 local place에서 무엇이 앞이고 뒤인가, 어떤 흐름이 intended progression과 양립하는가

이 분리가 중요한 이유는, local drivable support가 progression support를 조금 벗어나더라도 **주행 의미 자체는 사라지지 않아야 하기 때문**이다.

## progression이란 무엇인가

이 프로젝트에서 progression은 단순히 “ego heading 앞쪽”이나 “centerline 방향”을 뜻하지 않는다.

progression은 더 정확히는:

- 이 local place에서 무엇이 before이고 무엇이 after인가
- 어떤 흐름이 intended progression과 더 양립하는가
- 직선이면 직선 진행, bend면 휘어진 진행, split이면 여러 candidate continuation을 포함한 ordering

을 뜻한다.

즉 progression은 **공간 위에 앞/뒤 ordering을 부여하는 의미**이지, 곧바로 winner 방향을 강제하는 discrete action이 아니다.

## field는 공간을 알려주고, 방향 선택은 상위 layer가 한다

이 프로젝트가 만드는 field는 optimizer나 planner를 대신하지 않는다.

field의 역할:

- 어떤 영역이 더 높은 preference를 가지는지
- 같은 progression slice에서 중심이 더 좋은지
- 더 먼 progression gain이 가까운 중심 선호를 언제 이길 수 있는지
- branch나 continuity ambiguity가 어떤 spatial ordering을 만드는지

를 공간 전체의 ordering으로 알려주는 것이다.

반면 실제 방향 선택, winner 결정, control command는 상위 layer나 optimizer가 담당한다.

즉 이 field는 **공간을 알려주지 방향을 직접 고르지 않는다.**

## 자연 contour와 인공 artifact를 어떻게 구분하는가

이 프로젝트는 모든 contour를 없애려 하지 않는다.

허용하는 것:

- bend나 U-turn에서 보이는 대각선 contour
- 2D heatmap에서 비틀린 면처럼 보이는 global 등고선

제거 대상:

- active-set / neighborhood artifact가 만든 abrupt jump
- overlap 영역 ordering flip
- branch 사이의 hole
- visible endpoint가 semantic start/end처럼 보이는 fake end-cap

즉 기준은 “그림이 복잡해 보이느냐”가 아니라, **공간 기하에서 자연스럽게 나온 contour인지, 구현 artifact인지**다.

## SSC와의 관계

SSC는 이 아이디어를 실제로 적용해보는 중요한 validation source다.

하지만 SSC는 canonical truth가 아니다.

이 프로젝트는 다음 원칙을 유지한다.

- SSC는 downstream validation environment다
- SSC에서 필요한 요구사항은 evidence일 뿐, 곧바로 canonical truth로 승격하지 않는다
- 이 repo는 끝까지 **점수장 SSOT**를 유지하고, SSC는 그 결과를 적용해보는 하위 소비자다

즉 SSC는 중요하지만, **이 프로젝트가 SSC에 매몰되면 안 된다.**

## 현재 repo 상태

현재 이 repo는 다음 상태다.

- `Phase 5 완료`
- `Phase 6 준비 상태`

여기서 이미 정리된 것:

- canonical 문서 정리
- tiny evaluator와 toy case
- local raster visualization
- Parameter Lab compare workflow
- cached runtime query layer
- generic source adapter SSOT와 reference adapter
- debug component view와 profile inspection
- semantic-first acceptance lock

아직 여기서 하지 않는 것:

- Gazebo / RViz / MPPI hookup
- optimizer integration

즉 이 repo는 현재 **점수장 SSOT + morphology 연구용 랩 + downstream이 소비할 runtime contract** 역할을 가진다.

## 현재 기준 결론

한 줄로 요약하면:

`driving-preference-field`는 source-agnostic progression semantics와 drivable semantics를 받아, 현재 보이는 local map 전체에 대해 **whole-space preference field**를 정의하는 프로젝트다. 이 field는 공간의 ordering을 알려주고, 실제 방향 선택은 상위 layer가 하며, SSC 같은 downstream은 이 canonical field를 검증하는 소비자 역할을 한다.
