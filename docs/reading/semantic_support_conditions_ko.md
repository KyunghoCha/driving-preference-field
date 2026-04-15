# Semantic Support 조건 메모

작성일: 2026-04-16

## 문서 목적

이 문서는 최근 적용/대화 과정에서 다시 확인된 **semantic support 관련 사실과 미확정 항목**만 reading 수준으로 정리한다.

이 문서는 canonical truth를 새로 정의하지 않는다. 현재 canonical 기준은 design 문서를 따른다.

관련 canonical 문서:

- `docs/design/input_semantics_ko.md`
- `docs/design/source_adapter_ko.md`
- `docs/design/project_overview_ko.md`

## 현재 canonical 문서에서 이미 고정된 사실

- canonical input은 raw source가 아니라 **semantic contract**다
- canonical 입력의 최소 축은 `drivable semantics`와 `progression semantics`다
- canonical은 특정 geometry primitive를 필수 형식으로 강제하지 않는다
- canonical은 fixed source type이나 source-specific naming을 요구하지 않는다
- `ego_pose`는 snapshot 본체가 아니라 `QueryContext`에 속한다
- `local_window` 크기와 slicing policy는 canonical truth가 아니라 experiment 영역이다
- `support/confidence` transport shape와 exact weighting semantics는 experiment 영역이다
- branch winner는 canonical field가 직접 정하지 않는다

## 현재 대화에서 확인된 정보

- global path는 모든 적용 환경에서 항상 주어진다고 가정할 수 없다
- 따라서 transverse 또는 longitudinal support scope를 global로 고정하는 것은 current canonical truth가 아니다
- support scope는 source가 제공할 수 있는 progression support 형태에 따라 달라질 수 있다
- discrete source input 자체는 금지 조건이 아니다
- discrete nodes, edges, paths, polygons 같은 입력도 semantic support로 번역되면 사용할 수 있다
- source가 충분한 semantic quality로 `drivable support`와 `progression support`를 복원하지 못할 수 있다
- 이 경우 runtime이 소비할 수 있는 semantic input은 partial 또는 weak support가 된다

## 아직 fixed truth로 올리지 않은 항목

- transverse support를 global-conditioned, local-conditioned, hybrid 중 어느 범위로 둘지
- longitudinal support를 global-conditioned, local-conditioned, hybrid 중 어느 범위로 둘지
- support scope selection policy를 canonical contract로 고정할지 여부
- semantic support quality가 약할 때 field를 어떤 degrade mode로 소비할지

## 문서 경계

- 이 문서는 정보 정리용 reading note다
- 새 canonical 정의나 새 current implementation rule을 추가하지 않는다
- 이후 결정이 필요하면 design 문서로 별도 승격한다
