# 테스트 감사

이 감사는 `git ls-files 'tests/**'` 기준 tracked test 파일 14개를 확인한 결과를 정리한다.

## 현재 역할

- 환경/Qt 준비:
  - `conftest.py`
- semantic/runtime/rendering regression:
  - `test_channels.py`
  - `test_evaluator.py`
  - `test_field_runtime.py`
  - `test_rendering.py`
  - `test_visualization_scale.py`
- config/preset/tooling:
  - `test_config.py`
  - `test_presets.py`
  - `test_profile_inspection.py`
  - `test_parameter_lab.py`
- adapter/CLI/input:
  - `test_source_adapter.py`
  - `test_cli.py`
  - `test_toy_loader.py`
- documentation regression:
  - `test_phase5_adapter_docs.py`

## 실제 상태

- semantic 핵심은 꽤 잘 잠겨 있다.
  - morphology acceptance
  - evaluator/runtime parity
  - adapter input validation
  - Lab export/profile workflow
  - visualization scale contract
- Windows CI 이슈를 잡은 CLI regression도 포함돼 있다.
- docs regression 테스트는 링크 무결성과 핵심 표현을 지키는 데 유효하다.

## 문제 유형

### 1. 문서 테스트의 문자열 결합도

- `test_phase5_adapter_docs.py`는 중요한 핵심을 잘 지키지만,
  표현을 다듬는 라운드마다 자주 따라 바뀌어야 한다.
- 현재는 IA와 key truth를 함께 검사하고 있어,
  문서 글쓰기 개선과 구조 무결성 검사가 다소 엉켜 있다.

### 2. 대형 GUI 테스트의 유지 비용

- `test_parameter_lab.py`는 coverage가 넓고 가치가 크다.
- 동시에 문서/용어/copy가 조금만 바뀌어도 따라 수정될 수 있는 면이 있다.
- audit 관점에서는 필요한 테스트지만, 책임 분리가 중요하다.

### 3. audit 단계 산출물 검사가 아직 없다

- 이번 감사 전까지는
  - 새 글쓰기 원칙 문서
  - 외부 기준 문서
  - 파일군별 audit 문서
  를 검증하는 테스트가 없었다.

## 유지할 것

- semantic-first regression 철학
- evaluator/runtime parity 검증
- adapter loader / CLI validation
- docs 링크 무결성 검사
- Parameter Lab export/profile 회귀

## 수정이 필요한 것

- 이번 라운드 산출물을 검증하는 문서 테스트 추가
- 문서 테스트를 “핵심 truth 유지”와 “표현 구속”으로 더 분리할 준비
- 이후 explanation/reference 문체 재작성 때 과도한 exact-phrase 결합을 줄이는 방향 검토

## 보류할 것

- test suite 구조 재편
- GUI test 범위 축소
- runtime acceptance threshold 재조정

## 다음 재작성 우선순위

1. audit/principles 문서 존재와 링크를 검사하는 테스트 추가
2. 이후 문서 재작성 단계에서 docs tests를 역할별로 더 잘게 나누는 방향 검토
