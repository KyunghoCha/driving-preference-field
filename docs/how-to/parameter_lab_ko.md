# Parameter Lab 사용

Parameter Lab은 같은 semantic snapshot과 같은 effective local context 위에서 field 파라미터를 바꾸며 morphology를 비교하는 연구용 도구다. geometry를 편집하는 studio도 아니고, optimizer나 integration runtime을 붙이는 도구도 아니다. 목적은 current implementation을 반복 가능하게 비교하고 export로 남기는 데 있다.

## Prerequisite

- `conda activate driving-preference-field`
- repo root에서 `PYTHONPATH=src python -m driving_preference_field parameter-lab`
- toy case 또는 generic adapter input path 준비

## 실행

1. case 또는 generic adapter input path를 연다.
2. baseline preset과 candidate preset을 고른다.
3. 필요하면 case-level ego/window control을 적용한다.
4. `Single`, `Compare`, `Diff`, `Profile` 탭으로 morphology를 확인한다.
5. 필요하면 `Apply`로 파라미터 변경을 반영한다.

case 변경, case control apply/reset, preset load, baseline/candidate copy는 즉시 재계산될 수 있고, slider / spinbox / dropdown 같은 세부 파라미터 변경은 기본적으로 `staged edit -> Apply` 흐름으로 처리한다.

## baseline/candidate 비교 절차

1. 비교할 case를 고정한다.
2. baseline과 candidate에 각각 preset을 선택한다.
3. selected channel을 기준으로 `Single`, `Compare`, `Diff`를 본다.
4. 필요하면 `Profile` 탭에서 line cut / profile inspection을 같이 본다.
5. qualitative note를 남기고 export를 만든다.

Parameter Lab이 기본적으로 다루는 축은 longitudinal, transverse, support / gate다. score sign은 `higher is better`로 읽고, diff는 `candidate - baseline`으로 읽는다.

## Export 결과물

session export에는 최소한 다음이 남는다.

- case path
- selected channel
- effective ego pose
- effective local window
- baseline/candidate preset snapshot
- profile summary
- qualitative note
- summary metrics

profile inspection export에는 다음이 포함된다.

- `profile_baseline.png`
- `profile_candidate.png`
- `profile_diff.png`
- `profile_data.json`

비교 export는 preset snapshot, render set, profile bundle을 함께 남겨 동일 비교를 다시 추적할 수 있게 한다.

## 현재 구현 범위

현재 Parameter Lab은 다음을 포함한다.

- case 선택
- generic adapter input path 직접 열기
- case-level ego/window control
- baseline / candidate parameter 패널
- single / compare / diff view
- preset 저장 / 불러오기 / 복사
- summary metrics 표시
- qualitative note 입력
- comparison export
- fixed / normalized scale mode
- `progression_tilted` 기본 selected channel
- profile inspection 탭
- debug view (`s_hat`, `n_hat`, longitudinal/transverse/support/alignment component)

현재 GUI는 canonical 전체를 다 노출하지는 않지만, `progression_tilted`를 읽는 데 필요한 `Main`과 current implementation morphology를 다듬는 `Advanced Surface`를 함께 노출한다. drivable boundary는 overlay로 읽고, obstacle / rule / dynamic cost는 costmap 성격의 별도 채널로만 본다.

## 현재 파라미터 배치

현재 우측 `Parameters` 도크는 `Main`과 접이식 `Advanced Surface`를 함께 다룬다. `Main`에는 `ProgressionConfig`의 9개 항목이 들어 있고, field semantics를 바로 읽는 비교 실험에 필요한 knob를 담당한다.

`Advanced Surface`에는 anchor spacing, spline density, sigma min/scale, end extension, support/alignment modulation, transverse handoff smoothing 같은 항목이 들어간다. 이 항목들은 구현 품질과 성능에 영향을 주므로 기본적으로 접힌 상태로 두고, 연구용으로 필요할 때만 펼쳐서 조정하는 것이 맞다.

좌측 `Workspace`는 `Presets`, `Summary`, `Profile`, `Layers`처럼 결과를 읽는 공간으로 유지한다. `Advanced Surface`도 좌측 탭에 넣지 않고 우측 `Parameters` 도크 하단 접이식 섹션으로 둔다.

파라미터 분류와 hidden tunable 목록은 [파라미터 노출 정책](../explanation/parameter_exposure_policy_ko.md)과 [파라미터 카탈로그](../reference/parameter_catalog_ko.md)에서 canonical/current 기준으로 확인한다.

## Overlay와 Guide 읽기

cyan progression guide overlay는 current field가 아니라 raw input polyline을 그대로 그린다. 예를 들어 `sensor_patch_open`의 progression guide가 살짝 위로 기울어져 보이는 것은 렌더링 오류가 아니라 case 입력이 `[-0.5, 0.0] -> [2.5, 0.15]`로 정의돼 있기 때문이다.

따라서 guide overlay는 “입력이 무엇이었는가”를 보여주고, heatmap은 “그 입력으로부터 현재 field가 어떻게 읽혔는가”를 보여준다. 둘이 완전히 같은 모양일 필요는 없다.

## Profile 탭 읽기

`Profile` 탭은 baseline, candidate, diff를 각각 PNG preview와 line-cut 데이터로 보여준다. 그래프가 viewport보다 크면 스크롤로 확인하고, placeholder 상태에서는 텍스트만 보인다.

이 탭은 tuning panel이 아니라 inspection panel이다. profile line spec은 여기서 바꾸지만, field semantics를 바꾸는 parameter knob는 우측 `Parameters` 도크에만 둔다.

## 현재 제한사항

다음은 현재 Parameter Lab 범위에 포함하지 않는다.

- geometry 편집
- progression guide 편집
- region draw/edit
- source adapter 구현 자체
- Gazebo / RViz / MPPI integration
- studio canvas
- interactive drawing
- 3D preview 본체화

GUI/PNG raster는 local map 위에서 연속 함수를 샘플링한 결과이며, Parameter Lab은 downstream integration tool이 아니라 whole-space field morphology를 읽고 비교하는 해석 도구로 유지한다.
