# Src Audit

이 감사는 `git ls-files 'src/**'` 기준 tracked source 파일 34개를 확인한 결과를 정리한다.
범위는 core/runtime/adapter/cli/rendering/ui 전체다.

## 현재 역할

### Core / contracts / config

- `__init__.py`
- `__main__.py`
- `contracts.py`
- `config.py`
- `geometry.py`
- `channels.py`
- `exception_layers.py`
- `evaluator.py`

### Runtime / rendering / profiling

- `progression_surface.py`
- `field_runtime.py`
- `raster.py`
- `rendering.py`
- `visualization_scale.py`
- `profile_inspection.py`

### Adapter / input / CLI / presets

- `source_adapter.py`
- `input_loader.py`
- `toy_loader.py`
- `cli.py`
- `presets.py`
- `comparison_session.py`

### UI

- `ui/async_raster_evaluator.py`
- `ui/canvas_view.py`
- `ui/parameter_guide.py`
- `ui/parameter_lab_window.py`
- `ui/widgets/case_panel.py`
- `ui/widgets/color_scale_widget.py`
- `ui/widgets/layer_panel.py`
- `ui/widgets/preset_panel.py`
- `ui/widgets/profile_panel.py`
- `ui/widgets/progression_parameter_panel.py`
- `ui/widgets/summary_panel.py`
- `ui/widgets/text_viewer_dialog.py`

## 실제 상태

- 공개 계약과 핵심 용어는 대체로 문서와 맞는다.
  - `SemanticInputSnapshot`
  - `QueryContext`
  - `FieldRuntime`
  - `progression_tilted`
  - base / soft / hard 분리
- core/runtime 쪽 docstring은 현재 구현 의도를 비교적 분명히 적고 있다.
  - `progression_surface.py`
  - `field_runtime.py`
  - `exception_layers.py`
  - `evaluator.py`
- adapter 경로도 current design과 잘 맞는다.
  - `source_adapter.py`
  - `input_loader.py`
  - `toy_loader.py`
- UI는 기능적으로 풍부하지만,
  user-facing 텍스트와 tooltip이 문서보다 더 조밀하고 더 영어 혼합 비중이 높다.
  특히 `parameter_guide.py`는 설명 밀도가 높고 한 문자열에 많은 주장을 담는다.
- `parameter_lab_window.py`는 크고 역할이 많다.
  현재 audit 관점에서는 동작이 맞지만,
  이후 public-facing 주석과 user-facing copy를 고칠 때 가장 큰 작업면이 될 가능성이 높다.

## 문제 유형

### 1. public-facing 설명 텍스트의 밀도 차이

- 문서에서 다듬은 표현이 UI helper text와 tooltip에 그대로 반영되지 않은 구간이 있다.
- `parameter_guide.py`, `rendering.py`의 설명 문자열은 의미는 맞지만 사람 가독성이 높지 않다.

### 2. docstring/주석 분포의 불균형

- core/runtime는 현재 의도가 비교적 잘 드러난다.
- 일부 작은 모듈은 docstring이 없거나,
  파일 목적은 알 수 있어도 public contract까지는 드러나지 않는다.
- 이는 오류가 아니라, 다음 정리 단계에서 public-facing 주석 우선순위를 잡아야 한다는 신호다.

### 3. UI 모듈 결합도

- `parameter_lab_window.py`가 비교, 렌더링 상태, export, preset, profile, note를 모두 묶고 있다.
- 지금 바로 구조를 바꾸는 것은 범위 밖이지만,
  audit 기준으로는 “문서 재작성 이후 가장 큰 public-facing 정리 후보”다.

### 4. root-level terminology와의 미세한 톤 차이

- `README`와 explanation 문서는 현재 더 간결한 쪽으로 갔는데,
  UI와 rendering/channel description은 여전히 실험 도구의 내적 설명이 길게 남아 있다.

## 유지할 것

- contracts/config/evaluator/runtime의 현재 공개 용어
- adapter가 source-agnostic output contract를 유지하는 방식
- base / soft / hard 분리
- progression surface의 current implementation docstring과 runtime contract의 결합 방식
- CLI가 inspect/evaluate/render/adapter path를 같은 contract 위에서 제공하는 구조

## 수정이 필요한 것

- `parameter_guide.py`의 user-facing 설명 텍스트
- `rendering.py`의 channel description과 legend copy
- public-facing 주석 / CLI help / docstring 중 문서와 톤이 어긋나는 구간
- `parameter_lab_window.py` 주변의 큰 UI surface에서 용어와 문체 일관성

## 보류할 것

- 구조적 리팩터링
- UI 파일 분할
- current field formula 변경
- runtime contract 변경

## 다음 재작성 우선순위

1. 문서 재작성 완료 후 public-facing `src` 주석 / CLI help / docstring 정렬
2. `parameter_guide.py`와 `rendering.py`의 설명 텍스트 정리
3. 필요 시 `parameter_lab_window.py` 주변의 copy 정리
