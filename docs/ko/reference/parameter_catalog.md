# 파라미터 카탈로그

이 문서는 Parameter Lab의 파라미터 노출 구조를 한 번에 확인하는 찾아보기 문서다. 지금 무엇이 보이고, 무엇이 의도적으로 한 단계 뒤에 배치돼 있으며, 무엇이 끝까지 internal로 남는지를 같은 기준으로 정리한다.

## Main

`Main`은 사용자가 score semantics를 읽을 때 가장 먼저 만져야 하는 progression 파라미터다.

- `longitudinal_frame`
- `longitudinal_family`
- `longitudinal_peak`
- `longitudinal_gain`
- `lookahead_scale`
- `longitudinal_shape`
- `transverse_family`
- `transverse_peak`
- `transverse_shape`
- `transverse_falloff`
- `support_ceiling`

이 항목들은 우측 `Parameters` 도크에 항상 보이고, preset/config에도 같이 저장된다.

## Advanced

`Advanced Surface`는 현재 실제로 노출돼 있는 연구용 knob 모음이다. morphology 품질, discretization locality, support kernel, modulation을 더 세밀하게 조정할 때 쓰지만, `Main`보다 먼저 만질 대상은 아니다.

- discretization
  - `anchor_spacing_m`
  - `spline_sample_density_m`
  - `spline_min_subdivisions`
  - `end_extension_m`
- support kernel
  - `min_sigma_t`
  - `min_sigma_n`
  - `sigma_t_scale`
  - `sigma_n_scale`
- modulation
  - `support_base`
  - `support_range`
  - `alignment_base`
  - `alignment_range`
이 항목들은 구현 상수에서 config field로 승격됐고, 지금은 접힌 `Advanced Surface` 섹션에서 조정한다. 즉 “숨겨진 후보”가 아니라 “노출은 했지만 2단계로 밀어 둔 파라미터”로 읽는 것이 맞다.

## View / Tool 후보

overlay visibility, scale normalization, interpolation style, export presentation 같은 항목은 실제 knob가 될 수는 있지만 score semantics knob는 아니다. 이런 것들은 앞으로 `View` 계층으로 분리할 수 있어도, 이번 배치의 `Advanced Surface`에는 넣지 않았다.

## Internal

수치 안정성과 구현 안전장치에 가까운 값은 계속 internal로 남긴다. 대표 예시는 다음과 같다.

- `_EPS`
- `_EFFECTIVE_ANCHOR_WEIGHT_EPS`
- dominant guide tie-break 규칙
- surface cache/batch 같은 low-level helper 값

이 항목들은 존재를 숨기진 않지만 GUI control로 노출하지 않는다.

## 현재 기준

정책 설명은 [파라미터 노출 정책](../explanation/parameter_exposure_policy.md)에서 읽고, 이 문서에서는 현재 구조와 이름을 lookup하는 데 집중하는 것이 맞다.
