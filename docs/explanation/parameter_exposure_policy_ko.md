# 파라미터 노출 정책

이 문서는 `driving-preference-field`에서 어떤 tunable을 바로 GUI에 노출하고, 어떤 것은 숨겨 두며, 어떤 것은 끝까지 internal로 유지할지를 설명한다. 목적은 모든 상수를 한 번에 노출하는 것이 아니라, field semantics를 읽는 실험과 구현 내부의 미세 조정을 분리해 drift를 막는 것이다.

Parameter Lab은 현재 whole-space preference field의 morphology를 반복 가능하게 비교하는 연구 도구다. 그래서 우선 노출해야 하는 것은 사용자가 `progression_tilted`의 의미를 바로 읽고 바꿀 수 있는 항목이다. 반대로 anchor discretization, spline density, handoff smoothing 같은 항목은 구현 품질과 성능에 영향을 주므로, 기본 패널과 같은 레벨이 아니라 접이식 `Advanced Surface` 섹션으로 한 단계 낮춰 노출한다.

이 repo는 파라미터를 세 tier로 나눈다. `Main`은 현재 GUI에서 직접 실험해야 하는 canonical knob다. `Advanced`는 parameterization 가치가 있어 현재 GUI의 접이식 `Advanced Surface` 섹션으로 노출된 연구용 knob다. `Internal`은 구현 안정성이나 수치 안전을 위한 값으로 남겨 두고, 사용자-facing 도구에 올리지 않는다.

`Main`으로 올리는 기준은 분명해야 한다. 사용자가 field semantics를 읽을 때 mental model과 바로 연결되고, baseline/candidate 비교에서 자주 조정하며, 값을 바꾸는 이유를 설명할 수 있어야 한다. 지금 `ProgressionConfig`의 longitudinal, transverse, support ceiling 항목이 여기에 들어간다.

`Advanced`는 `Main`과 같은 급의 기본 패널은 아니지만, 현재는 우측 `Parameters` 도크 하단의 접이식 섹션으로 노출된다. morphology를 더 매끈하게 하거나 성능을 튜닝할 때 의미가 있지만, 잘못 만지면 field 의미보다 구현 artifact를 먼저 바꿔 버릴 수 있다. anchor spacing, spline density, sigma min/scale, end extension, support/alignment modulation, transverse handoff smoothing 상수는 이 tier가 맞다.

`Internal`은 존재를 문서에서 숨기지 않지만, GUI 노출 대상은 아니다. numerical epsilon, batch/cache, low-level guard constant처럼 구현이 깨지지 않게 유지하는 값은 사용자가 실험 knob로 읽어서는 안 된다. 이런 항목까지 같은 레벨로 노출하면 도구가 해석 도구가 아니라 debugging console로 바뀐다.

새 knob를 추가로 노출할 때는 먼저 reference catalog에 등록해야 한다. 그다음 이 knob가 `Main`인지, `Advanced` 후보인지, 끝까지 `Internal`로 둘지를 판단한다. 구현에 상수가 있다는 이유만으로 바로 slider를 만들지 않는다.

현재 UI 배치도 이 정책을 따른다. 좌측 `Workspace`는 `Presets`, `Summary`, `Profile`, `Layers`처럼 결과를 읽는 공간이다. 우측 `Parameters` 도크는 조정 공간이고, `Main`과 접이식 `Advanced Surface`를 함께 둔다. 좌측 읽기 공간을 tuning panel로 바꾸는 것은 피한다.

이 정책은 숨기기 위한 정책이 아니다. 사용자가 바로 읽어야 하는 의미를 먼저 드러내고, 구현 품질·성능·시각화 노이즈를 만드는 knob는 한 단계 뒤로 미루자는 정책이다. 이렇게 해야 Parameter Lab이 field semantics 비교 도구로 남고, current implementation의 미세 상수 때문에 canonical 의미가 흔들리지 않는다.
