# driving-preference-field

[English README](./README.md)

[![ci](https://github.com/KyunghoCha/driving-preference-field/actions/workflows/ci.yml/badge.svg)](https://github.com/KyunghoCha/driving-preference-field/actions/workflows/ci.yml)

`driving-preference-field`는 현재 보이는 local map 전체에 대해 whole-space driving preference field를 정의하고 시험하는 연구용 워크스페이스다. 현재 상태는 `Phase 5 완료, Phase 6 준비`다.

## 이 레포가 맡는 일

- progression-centered field semantics와 runtime contract를 canonical 기준으로 유지한다.
- Parameter Lab에서 morphology 비교 실험을 반복 가능하게 만든다.
- source adapter contract를 generic하게 유지해 downstream consumer가 재사용할 수 있게 한다.

현재 범위 밖인 것은 planner integration, Gazebo/RViz hookup, 전체 downstream control loop다.

## 준비 사항

- [environment.yml](./environment.yml)로 만드는 Python/conda 환경
- 권장 환경 이름: `driving-preference-field`
- 현재 안정적으로 확인한 NumPy 버전: `1.26.4`

## 빠른 시작

1. `conda env create -f environment.yml`
2. `conda activate driving-preference-field`
3. `PYTHONPATH=src python -m driving_preference_field parameter-lab`

## 문서

- 언어 선택 포털: [docs/index.md](./docs/index.md)
- 영어 포털: [docs/en/index.md](./docs/en/index.md)
- 한국어 포털: [docs/ko/index.md](./docs/ko/index.md)

처음 읽는 순서:

1. [프로젝트 개요](./docs/ko/explanation/project_overview.md)
2. [운영 원칙](./docs/ko/explanation/engineering_operating_principles.md)
3. [Base Field 기초](./docs/ko/explanation/base_field_foundation.md)
4. [소스 어댑터](./docs/ko/reference/source_adapter.md)
5. [런타임 계약](./docs/ko/reference/runtime_evaluation_contract.md)
6. [로드맵](./docs/ko/status/roadmap.md)

## Parameter Lab

Parameter Lab은 같은 local map sample 위에서 Baseline과 Candidate progression 설정을 비교하는 주 실험 UI다. 상단 툴바에서 영어/한국어를 전환할 수 있고, `Guide`와 `Parameter Help`도 현재 언어에 맞는 문서를 연다.

## 현재 범위

- canonical 문서와 계약
- progression surface morphology 실험
- preset, export, comparison tooling
- source에 종속되지 않는 semantic 입력 로딩

## 참고

- 현재 구현 수식: [docs/ko/reference/current_formula_reference.md](./docs/ko/reference/current_formula_reference.md)
- 외부 참고 로그: [docs/ko/reading/references/external_references.md](./docs/ko/reading/references/external_references.md)
