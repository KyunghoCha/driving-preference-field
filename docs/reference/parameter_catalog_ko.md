# 파라미터 카탈로그

이 문서는 Parameter Lab과 `progression_surface.py`에서 현재 조정 가능하거나 조정 후보인 항목을 한 곳에 모아 둔 lookup 문서다. 여기서 고정하는 것은 구현 상수의 존재 사실과 분류이며, `Advanced` 항목은 현재 우측 `Parameters` 도크의 접이식 `Advanced Surface` 섹션으로 노출된다.

## Main

다음 항목은 현재 `ProgressionConfig`에 들어 있고, 우측 `Parameters` 도크에서 직접 조정할 수 있다.

| 이름 | 상태 | 현재 노출 | 기본값 | 의미 | 영향 | 코드 위치 |
| --- | --- | --- | --- | --- | --- | --- |
| `longitudinal_frame` | Main | 예 | `local_absolute` | longitudinal tilt를 local-map progress로 읽을지, ego 기준 앞쪽 progress로 읽을지 정한다. | ordering, ahead bias | `src/driving_preference_field/config.py` |
| `longitudinal_family` | Main | 예 | `tanh` | progression axis를 따라 score를 키우는 함수 family다. | shape, ordering | `src/driving_preference_field/config.py` |
| `longitudinal_gain` | Main | 예 | `1.0` | transverse 위에 더해지는 longitudinal tilt의 세기다. | ordering, shape | `src/driving_preference_field/config.py` |
| `lookahead_scale` | Main | 예 | `0.25` | `ego_relative` frame에서 ahead gain이 얼마나 빨리 포화되는지 정한다. | ordering | `src/driving_preference_field/config.py` |
| `longitudinal_shape` | Main | 예 | `1.0` | longitudinal family의 곡률과 nonlinearity를 조절한다. | shape, ordering | `src/driving_preference_field/config.py` |
| `transverse_family` | Main | 예 | `exponential` | 같은 progression slice에서 center-high profile을 만드는 횡방향 함수 family다. | shape | `src/driving_preference_field/config.py` |
| `transverse_scale` | Main | 예 | `1.0` | 중심 ridge가 횡방향으로 얼마나 넓게 퍼지는지 정한다. | shape | `src/driving_preference_field/config.py` |
| `transverse_shape` | Main | 예 | `1.0` | transverse family의 곡률을 정한다. | shape | `src/driving_preference_field/config.py` |
| `support_ceiling` | Main | 예 | `1.0` | guide weight와 confidence가 support modulation에 줄 수 있는 상한이다. | shape, ordering | `src/driving_preference_field/config.py` |

## Advanced

다음 항목은 parameterization 가치가 커서 현재 `Advanced Surface` 섹션으로 노출된다. morphology와 성능, 시각화 artifact에 영향을 줄 수 있으므로 `Main`보다 한 단계 낮은 연구용 knob로 읽는다.

| 이름 | 상태 | 현재 노출 | 기본값 | 의미 | 영향 | 코드 위치 |
| --- | --- | --- | --- | --- | --- | --- |
| `_ANCHOR_SPACING_M` | Advanced | 예 | `0.20` | guide anchor를 몇 m 간격으로 놓을지 정한다. | 성능, shape | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_SPLINE_SAMPLE_DENSITY_M` | Advanced | 예 | `0.05` | resampled polyline을 만들 때 세그먼트 사이를 얼마나 촘촘히 densify할지 정한다. | 성능, shape | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_SPLINE_MIN_SUBDIVISIONS` | Advanced | 예 | `8` | 짧은 세그먼트에서도 최소 subdivision 개수를 유지한다. | 성능, shape | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_MIN_SIGMA_T` | Advanced | 예 | `0.40` | longitudinal Gaussian support의 최소 폭이다. | shape, robustness | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_MIN_SIGMA_N` | Advanced | 예 | `0.35` | lateral Gaussian support의 최소 폭이다. | shape, robustness | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_SIGMA_T_SCALE` | Advanced | 예 | `0.35` | guide length와 lookahead를 longitudinal sigma로 바꾸는 scale이다. | shape, ordering | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_SIGMA_N_SCALE` | Advanced | 예 | `1.50` | `transverse_scale`를 lateral sigma로 바꾸는 scale이다. | shape | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_END_EXTENSION_M` | Advanced | 예 | `2.0` | guide 끝에 virtual continuation anchor를 얼마나 연장할지 정한다. | shape, edge behavior | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_SUPPORT_BASE` | Advanced | 예 | `0.95` | support modulation의 바닥값이다. | shape, ordering | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_SUPPORT_RANGE` | Advanced | 예 | `0.05` | support quality가 modulation에 줄 수 있는 변화량이다. | shape, ordering | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_ALIGNMENT_BASE` | Advanced | 예 | `0.95` | heading alignment modulation의 바닥값이다. | shape, ordering | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_ALIGNMENT_RANGE` | Advanced | 예 | `0.05` | alignment quality가 modulation에 줄 수 있는 변화량이다. | shape, ordering | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_TRANSVERSE_HANDOFF_SUPPORT_RATIO` | Advanced | 예 | `0.25` | handoff candidate guide를 고를 때 dominant support 대비 최소 비율이다. | shape, 시각화 | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_TRANSVERSE_HANDOFF_SCORE_DELTA` | Advanced | 예 | `0.20` | handoff candidate guide를 고를 때 dominant score와 허용 차이다. | shape, 시각화 | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |
| `_TRANSVERSE_HANDOFF_TEMPERATURE` | Advanced | 예 | `0.05` | transverse handoff smoothing의 soft weighting temperature다. | shape, 시각화 | `src/driving_preference_field/config.py`, `src/driving_preference_field/progression_surface.py` |

이 항목들은 field semantics를 바로 바꾸는 것보다 current implementation의 morphology와 품질을 미세 조정하는 성격이 강하다. 그래서 현재는 `Main`과 분리된 접이식 `Advanced Surface` 섹션으로 노출한다.

## View / Tool 후보

다음은 field semantics보다 도구 사용성과 시각화 품질에 가까운 항목이다. 아직 public config나 GUI knob는 아니지만, 필요하면 향후 `Advanced` 또는 `View` 영역 후보가 될 수 있다.

| 이름 | 상태 | 현재 노출 | 기본값 | 의미 | 영향 | 코드 위치 |
| --- | --- | --- | --- | --- | --- | --- |
| overlay visibility (`progression_guides`, `drivable_boundary`, `ego_pose`, `hard_masks`) | Internal | 부분 노출 | case별 current state | overlay를 켜고 끄는 UI 상태다. | 시각화 | `src/driving_preference_field/ui/widgets/layer_panel.py` |
| channel selector | Main | 예 | `progression_tilted` | 어떤 raster channel을 보는지 정한다. | 시각화 | `src/driving_preference_field/ui/parameter_lab_window.py` |
| scale mode (`fixed`, `normalized`) | Main | 예 | `fixed` | heatmap 범위를 고정할지 현재 화면 범위로 정규화할지 정한다. | 시각화 | `src/driving_preference_field/ui/parameter_lab_window.py` |
| compare layout (`stacked`, `side_by_side`) | Internal | 부분 노출 | `stacked` | Compare 탭의 splitter 방향이다. | 시각화 | `src/driving_preference_field/ui/parameter_lab_window.py` |

## Internal

다음 항목은 존재를 숨기지 않지만 GUI 노출 대상이 아니다. numerical safety, low-level selection, cache, internal helper에 가깝다.

| 이름 | 상태 | 현재 노출 | 기본값 | 의미 | 영향 | 코드 위치 |
| --- | --- | --- | --- | --- | --- | --- |
| `_EPS` | Internal | 아니오 | internal constant | divide-by-zero와 comparison guard를 막는 epsilon이다. | 수치 안정성 | `src/driving_preference_field/progression_surface.py` |
| `_EFFECTIVE_ANCHOR_WEIGHT_EPS` | Internal | 아니오 | internal constant | effective anchor count를 셀 때 쓰는 guard다. | debugging only | `src/driving_preference_field/progression_surface.py` |
| tie-break (`score` 우선, `support` 보조) | Internal | 아니오 | hard-coded | dominant guide 선택 규칙이다. | ordering semantics | `src/driving_preference_field/progression_surface.py` |
| surface cache size (`lru_cache`) | Internal | 아니오 | `32` | surface signature cache 크기다. | 성능 | `src/driving_preference_field/progression_surface.py` |

## 현재 기준

지금 Parameter Lab은 `Main`과 접이식 `Advanced Surface`를 직접 조정한다. `Internal`은 문서로만 존재를 알리고 도구 knob로 승격하지 않는다.
