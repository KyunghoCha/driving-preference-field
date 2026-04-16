# Parameter Lab Guide

이 문서는 Parameter Lab을 실제로 어떻게 쓰는지 설명한다. 여기서 답하려는 질문은 세 가지다. 이 도구가 무엇을 위한 것인지, baseline과 candidate를 어떻게 비교하는지, 화면에 보이는 heatmap과 guide를 어떻게 읽어야 하는지다.

Parameter Lab은 geometry를 편집하는 studio가 아니다. 같은 semantic snapshot과 같은 effective local context 위에서 field 파라미터를 바꾸며 morphology를 비교하고, 그 비교를 export로 남기는 연구용 도구다.

## 이 문서가 필요한 경우

- 앱을 처음 열었는데 어디서 시작해야 할지 모르겠을 때
- `Single`, `Compare`, `Diff`, `Profile` 중 무엇을 먼저 봐야 할지 정하고 싶을 때
- `Docs`와 `Parameter Help`의 역할 차이를 알고 싶을 때
- preset, channel, scale, export가 각각 무엇을 바꾸는지 확인하고 싶을 때

## 빠른 시작

1. `conda activate driving-preference-field`
2. repo root에서 `PYTHONPATH=src python -m driving_preference_field parameter-lab`
3. case를 고른다.
4. baseline preset과 candidate preset을 고른다.
5. `progression_tilted`를 `Fixed` scale로 먼저 본다.
6. 필요하면 우측 `Parameters`에서 한 항목만 바꾸고 `Apply`를 누른다.
7. `Diff`와 `Profile`로 확인한 뒤 `Export Comparison`으로 비교를 저장한다.

실무적으로는 한 번에 한 변수만 바꾸는 편이 좋다. case, ego/window, preset, parameter를 동시에 바꾸면 차이의 원인을 읽기 어렵다.

## 화면 읽기

### 상단 툴바

상단 툴바는 자주 쓰는 액션만 둔다.

- `Reload Case`
  - 현재 case를 다시 읽고 비교를 다시 계산한다.
- `Export Comparison`
  - 현재 baseline/candidate 비교, preset snapshot, profile 결과를 함께 export한다.
- `Reset View`
  - 현재 canvas의 pan/zoom만 초기화한다.
- `channel`
  - 지금 볼 채널을 고른다.
- `scale`
  - 색의 의미를 고른다.
- `Guide`
  - 이 문서를 앱 안에서 연다.

기본 shortcut은 다음과 같다.

- `F5`: Reload Case
- `Ctrl+Shift+E`: Export Comparison
- `Ctrl+0`: Reset View
- `F1`: Guide

### 좌측 Workspace

좌측 `Workspace`는 결과를 읽는 공간이다.

- `Presets`
  - baseline/candidate preset을 고르고 저장하고 복사한다.
- `Summary`
  - 현재 비교 상태를 요약해서 보여준다.
- `Profile`
  - line cut과 profile PNG를 본다.
- `Layers`
  - overlay visibility를 켜고 끈다.

좌측은 읽는 공간이다. 파라미터 조정은 우측 `Parameters` 도크에서만 한다.

### 우측 Parameters

우측 `Parameters`는 조정 공간이다.

- `Main`
  - field semantics를 직접 읽을 때 먼저 만지는 항목이다.
- `Advanced Surface`
  - morphology, discretization, kernel, handoff 같은 구현 품질 튜닝 항목이다.

규칙은 단순하다. 먼저 `Main`으로 의미를 잡고, 그래도 split/merge, bend, locality 같은 품질 문제가 남을 때만 `Advanced Surface`를 연다.

## 먼저 무엇을 봐야 하나

### 1. `progression_tilted`

항상 `progression_tilted`를 먼저 본다. 이 채널이 현재 base field의 대표 score다. canonical score sign은 `higher is better`다.

### 2. `Fixed` scale

처음에는 `Fixed` scale을 쓴다. baseline과 candidate가 같은 색-값 대응을 공유하므로 비교가 쉬워진다. `Normalized`는 탐색용 보조 모드다.

### 3. `Diff`

`Diff`는 항상 `candidate - baseline`이다. diff가 양수면 candidate가 더 높고, 음수면 baseline이 더 높다.

### 4. guide overlay

cyan progression guide는 현재 field가 아니라 raw input polyline이다. 예를 들어 `sensor_patch_open`의 guide가 약간 기울어져 보이는 것은 rendering bug가 아니라 입력이 `[-0.5, 0.0] -> [2.5, 0.15]`로 정의돼 있기 때문이다.

## 자주 하는 작업

### baseline과 candidate 비교

1. 같은 case를 유지한다.
2. baseline preset과 candidate preset을 고른다.
3. `progression_tilted`를 `Fixed` scale로 본다.
4. `Compare`에서 morphology 차이를 본다.
5. `Diff`에서 차이 방향을 본다.
6. 필요하면 `Profile`에서 line cut을 본다.

### 파라미터 한 개만 바꿔 보기

1. 우측 `Parameters`에서 한 항목만 바꾼다.
2. 바로 계산되지 않는다. `Apply`를 눌러야 반영된다.
3. 결과가 마음에 들지 않으면 `Reset`으로 패널 값을 되돌린다.

case 변경, case control apply/reset, preset load, baseline/candidate copy는 즉시 재계산될 수 있다. 반대로 spinbox, dropdown 같은 세부 파라미터 편집은 `staged edit -> Apply` 흐름이다.

### split, merge, bend 읽기

- split/merge는 `multiple progression guides`로 표현한다.
- raster는 continuous field를 local map 위에서 샘플링한 결과다.
- guide overlay와 heatmap이 같은 모양일 필요는 없다.
- split 직전이나 merge 직전 shape가 입력 semantics의 결과인지, tuning artifact인지 먼저 나눠 본다.

### profile 보기

`Profile` 탭은 tuning panel이 아니라 inspection panel이다. baseline, candidate, diff를 각각 PNG preview와 line-cut 데이터로 보여준다. 그래프가 viewport보다 크면 스크롤로 읽는다.

## Guide와 Parameter Help의 차이

둘은 역할이 다르다.

- `Guide`
  - 이 도구를 어디서 시작하고, 무엇을 보고, 어떤 순서로 쓰는지 설명한다.
- `Parameter Help`
  - 우측 `Parameters` 패널의 각 knob가 무엇을 바꾸는지 설명한다.

즉, “이 화면에서 지금 무엇을 해야 하는가”는 `Guide`가 답하고, “이 파라미터를 올리면 무엇이 바뀌는가”는 `Parameter Help`가 답한다.

## Export로 남는 것

comparison export에는 최소한 다음이 남는다.

- case path
- selected channel
- effective ego pose
- effective local window
- baseline/candidate preset snapshot
- summary metrics
- profile summary
- qualitative note

profile inspection export에는 다음이 포함된다.

- `profile_baseline.png`
- `profile_candidate.png`
- `profile_diff.png`
- `profile_data.json`

즉 export는 스크린샷 한 장이 아니라, 같은 비교를 다시 복원할 수 있는 bundle이다.

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

GUI/PNG raster는 local map 위에서 연속 함수를 샘플링한 결과다. Parameter Lab은 downstream integration tool이 아니라 whole-space field morphology를 읽고 비교하는 해석 도구로 유지한다.

## 더 읽을 문서

- [파라미터 노출 정책](../explanation/parameter_exposure_policy_ko.md)
- [파라미터 카탈로그](../reference/parameter_catalog_ko.md)
- [프로젝트 개요](../explanation/project_overview_ko.md)
- [Base Field 기초](../explanation/base_field_foundation_ko.md)
