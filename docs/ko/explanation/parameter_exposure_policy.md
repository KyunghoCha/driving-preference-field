# 파라미터 노출 정책

이 문서는 어떤 tunable을 바로 GUI에 노출하고, 어떤 것은 숨겨 두며, 어떤 것은 끝까지 internal로 유지할지를 설명한다. 질문은 단순하다. “코드 안에 상수가 있으니 slider를 만들자”가 아니라, 사용자가 무엇을 직접 읽고 조정해야 하는가를 어떻게 구분할 것인가다.

Parameter Lab은 현재 whole-space preference field의 morphology를 반복 가능하게 비교하는 연구 도구다. 그래서 먼저 노출해야 하는 것은 field semantics를 직접 읽는 knob다. 반대로 discretization, kernel, handoff smoothing 같은 항목은 구현 품질과 성능에 영향을 주므로, 같은 급의 기본 패널이 아니라 한 단계 낮은 연구용 섹션으로 두는 편이 맞다.

이 repo는 파라미터를 세 tier로 나눈다.

- `Main`
  - field semantics를 직접 읽는 canonical knob
- `Advanced`
  - parameterization 가치는 있지만 구현 품질과 성능 tuning에 가까운 연구용 knob
- `Internal`
  - 수치 안정성과 구현 세부를 위한 값으로, GUI에 올리지 않는 항목

`Main`으로 올리는 기준은 분명해야 한다. 사용자가 값을 바꾸는 이유를 설명할 수 있고, baseline/candidate 비교에서 자주 만지며, field의 의미를 바로 읽는 데 연결돼야 한다. 지금 `ProgressionConfig`의 longitudinal, transverse, support ceiling 항목이 여기에 들어간다.

`Advanced`는 숨기기 위한 tier가 아니다. 현재는 우측 `Parameters` 도크 하단의 접이식 `Advanced Surface` 섹션으로 노출돼 있다. split/merge handoff, bend locality, discretization fidelity, modulation strength처럼 morphology 품질을 다듬을 때는 필요하지만, 잘못 만지면 semantics보다 implementation artifact를 먼저 바꿔 버릴 수 있다. anchor spacing, spline density, sigma min/scale, end extension, support/alignment modulation, transverse handoff smoothing 상수가 이 tier에 속한다.

`Internal`은 존재를 문서에서 숨기지 않지만, GUI 노출 대상은 아니다. numerical epsilon, batch/cache, low-level guard constant처럼 구현이 깨지지 않게 유지하는 값은 사용자가 실험 knob로 읽어서는 안 된다. 이런 항목까지 같은 레벨로 노출하면 도구가 해석 도구가 아니라 debugging console로 바뀐다.

새 knob를 노출할 때는 먼저 reference catalog에 등록해야 한다. 그 다음 이 knob가 `Main`인지, `Advanced`인지, 끝까지 `Internal`로 둘지를 판단한다. 구현에 상수가 있다는 이유만으로 바로 panel control을 추가하지 않는다.

현재 UI 배치도 이 정책을 따른다. 좌측 `Workspace`는 `Presets`, `Summary`, `Profile`, `Layers`처럼 결과를 읽는 공간이다. 우측 `Parameters` 도크는 조정 공간이고, `Main`과 접이식 `Advanced Surface`를 함께 둔다. 좌측 읽기 공간을 tuning panel로 바꾸는 것은 피한다.

이 정책의 목적은 숨기는 것이 아니라, 먼저 드러나야 할 의미를 우선순위대로 드러내는 것이다. 이렇게 해야 Parameter Lab이 field semantics 비교 도구로 남고, current implementation의 미세 상수 때문에 canonical 의미가 흔들리지 않는다.
