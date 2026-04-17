<a id="parameter-lab-guide"></a>
# Parameter Lab 안내

이 문서는 Parameter Lab 안에서 어디서 시작하고 무엇을 먼저 봐야 하는지 빠르게 설명한다. 핵심 질문은 세 가지다. 이 도구가 무엇을 위한 것인지, 어디서 시작해야 하는지, 그리고 지금 화면을 어떻게 읽어야 하는지다.

Parameter Lab은 geometry 편집기가 아니다. 같은 semantic snapshot과 같은 effective local context 위에서 field morphology를 비교하고, 그 비교를 export bundle로 남기는 해석 도구다.

<a id="what-this-tool-is-for"></a>
## 이 도구는 무엇을 하는가

- 같은 case 위에서 `Baseline`과 `Candidate`를 비교한다.
- `progression_tilted`와 debug channel을 같은 local map 위에서 읽는다.
- 입력 geometry를 바꾸지 않고 split, merge, bend, multilane 거동을 본다.
- 나중에 다시 열 수 있는 comparison bundle을 export한다.

<a id="start-here"></a>
## 먼저 여기서 시작

처음에는 아래 순서를 그대로 따르면 된다.

1. case 하나를 고르고 양쪽에 그대로 유지한다.
2. `progression_tilted`를 `Fixed` scale로 읽는다.
3. `Main`에서 한 항목만 바꾸고 `Apply`를 누른 뒤 `Diff`를 본다.

“이 화면에서 지금 무엇을 해야 하는가”는 `Guide`가 답한다. “이 knob를 올리면 무엇이 바뀌는가”는 `Parameter Help`가 답한다.

<a id="quick-actions"></a>
## 빠른 액션

가장 짧은 시작 경로는 이렇다.

1. `conda activate driving-preference-field`
2. repo root에서 `PYTHONPATH=src python -m driving_preference_field parameter-lab`
3. case를 고른다.
4. baseline preset과 candidate preset을 고른다.
5. `progression_tilted`를 `Fixed` scale로 본다.
6. 파라미터 하나를 바꾸고 `Apply`를 누른다.
7. `Diff`로 확인한 뒤 `Export Comparison`으로 저장한다.

기본 shortcut:

- `F5`: Reload Case
- `Ctrl+Shift+E`: Export Comparison
- `Ctrl+0`: Reset View
- `F1`: Guide

<a id="how-to-read-the-screen"></a>
## 화면 읽기

<a id="top-toolbar"></a>
### 상단 툴바

상단 툴바에는 자주 쓰는 액션만 둔다.

- `Reload Case`: 현재 case를 다시 읽고 비교를 다시 계산한다.
- `Export Comparison`: 현재 baseline/candidate 비교 bundle을 저장한다.
- `Reset View`: 현재 canvas의 pan/zoom을 초기화한다.
- `channel`: 지금 볼 raster channel을 고른다.
- `scale`: 색 범위를 어떻게 읽을지 고른다.
- `language`: 앱, `Guide`, `Parameter Help`를 영어/한국어로 전환한다.
- `Guide`: 이 문서를 앱 안에서 연다.

<a id="workspace"></a>
### `Workspace`

좌측 `Workspace`는 결과를 읽는 공간이다.

- `Presets`: baseline/candidate preset을 고르고 저장하고 복사한다.
- `Summary`: 현재 비교 상태를 요약해서 본다.
- `Profile`: line cut과 preview plot을 본다.
- `Layers`: overlay visibility를 조절한다.

좌측은 읽는 공간이고, 우측은 조정 공간이다.

<a id="parameters"></a>
### `Parameters`

우측 `Parameters`는 조정 공간이다.

- `Main`: field semantics를 읽을 때 먼저 쓰는 항목
- `Advanced Surface`: morphology 품질, discretization, support kernel, weak modulation을 다룰 때 여는 항목

규칙은 단순하다. 먼저 `Main`으로 semantics를 잡고, 그래도 품질 문제가 남을 때만 `Advanced Surface`를 연다.

<a id="canvas-views"></a>
### canvas 보기

raster는 continuous field를 local map 위에서 샘플링한 결과다. field contract 자체가 아니다.

- `Single`: 한 쪽을 단독으로 본다.
- `Compare`: morphology 차이를 나란히 본다.
- `Diff`: `candidate - baseline` 차이만 본다.

cyan progression guide overlay는 field 자체가 아니라 raw input polyline이다. `sensor_patch_open`에서 약간 기울어져 보이는 것은 rendering bug가 아니라 입력 정의 자체다.

<a id="common-tasks"></a>
## 자주 하는 작업

<a id="compare-baseline-and-candidate"></a>
### `Baseline`과 `Candidate` 비교

1. 같은 case를 유지한다.
2. baseline preset과 candidate preset을 고른다.
3. `progression_tilted`를 `Fixed` scale로 본다.
4. `Compare`에서 morphology를 본다.
5. `Diff`에서 부호와 크기를 본다.
6. 필요하면 `Profile`에서 line cut을 본다.

<a id="change-one-parameter"></a>
### 파라미터 하나만 바꾸기

1. 우측 `Parameters`에서 한 항목만 바꾼다.
2. `Apply`를 눌러 staged edit를 반영한다.
3. 취소하려면 `Reset`을 누른다.

case 변경, case control apply/reset, preset load, baseline/candidate copy는 바로 재계산될 수 있다. 반대로 세부 파라미터는 `staged edit -> Apply` 흐름이다.

<a id="read-split-merge-and-bend-cases"></a>
### split, merge, bend 읽기

- split/merge는 `multiple progression guides`로 표현한다.
- heatmap과 guide overlay가 같은 모양일 필요는 없다.
- split/merge의 모양은 입력 semantics 때문일 수도 있고 tuning artifact 때문일 수도 있다.
- shape를 버그로 보기 전에 이 둘을 먼저 나눠서 본다.

<a id="read-profiles"></a>
### `Profile` 읽기

`Profile`은 tuning panel이 아니라 inspection panel이다. baseline, candidate, diff를 line-cut 데이터와 preview plot으로 보여준다. preview가 viewport보다 크면 스크롤해서 읽는다.

<a id="export"></a>
## 내보내기

`Export Comparison`에는 최소한 다음이 들어간다.

- case path
- selected channel
- effective ego pose
- effective local window
- baseline/candidate preset snapshot
- summary metrics
- profile summary
- qualitative note

profile inspection export에는 다음도 포함된다.

- `profile_baseline.png`
- `profile_candidate.png`
- `profile_diff.png`
- `profile_data.json`

즉 export는 스크린샷이 아니라, 같은 비교를 다시 검토할 수 있는 bundle이다.
앱은 export 전에 확인을 한 번 더 묻는다. 파일 시스템에 결과를 쓰고 잠시 시간이 걸릴 수 있기 때문이다.

<a id="limits"></a>
## 제한사항

현재 Parameter Lab 범위에 포함하지 않는 것은 다음과 같다.

- geometry 편집
- progression guide 편집
- region draw/edit
- source adapter 구현 자체
- Gazebo / RViz / MPPI integration
- studio canvas
- interactive drawing
- full 3D preview tooling

이 도구는 local map 위에서 whole-space field morphology를 읽고 비교하는 데 집중한다.

<a id="read-next"></a>
## 더 읽을 문서

- [파라미터 노출 정책](../explanation/parameter_exposure_policy.md)
- [파라미터 카탈로그](../reference/parameter_catalog.md)
- [프로젝트 개요](../explanation/project_overview.md)
- [Base Field 기초](../explanation/base_field_foundation.md)
