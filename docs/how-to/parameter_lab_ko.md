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

현재 GUI는 canonical 전체를 다 노출하지는 않는다. progression frame, longitudinal, transverse, support ceiling 축을 직접 다루는 compare tool에 집중돼 있다. drivable boundary와 branch guide는 overlay로 읽고, safety / rule / dynamic burden은 costmap 성격의 별도 채널로만 본다.

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
