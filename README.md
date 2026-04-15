# driving-preference-field

[![ci](https://github.com/KyunghoCha/driving-preference-field/actions/workflows/ci.yml/badge.svg)](https://github.com/KyunghoCha/driving-preference-field/actions/workflows/ci.yml)

source-agnostic progression semantics와 drivable semantics를 받아, 현재 보이는 local map 전체를 평가하는 whole-space driving preference field를 정의하고 실험하는 연구 워크스페이스다.

현재 상태는 `Phase 5 완료, Phase 6 준비 상태`다.

처음 보는 사람은 아래 순서로 읽으면 된다.

1. `docs/explanation/project_overview_ko.md`
2. `docs/explanation/engineering_operating_principles_ko.md`
3. `docs/explanation/base_field_foundation_ko.md`
4. `docs/reference/source_adapter_ko.md`
5. `docs/reference/runtime_evaluation_contract_ko.md`
6. `docs/status/roadmap_ko.md`

문서 포털과 전체 IA는 `docs/index.md`에 정리돼 있다.

## 빠른 시작

1. `conda env create -f environment.yml`
2. `conda activate driving-preference-field`
3. `PYTHONPATH=src python -m driving_preference_field parameter-lab`

## 현재 범위

- 이 repo는 점수장 SSOT, morphology 연구용 랩, runtime/adapter contract를 유지한다
- `FieldRuntime`와 source adapter는 downstream consumer가 그대로 사용할 수 있는 public contract를 제공한다
- Gazebo / RViz / MPPI hookup, planner integration, interactive studio는 현재 범위가 아니다

## 참고

- 문서 포털: `docs/index.md`
- external reference log: `docs/reading/references/external_references_ko.md`
- current implementation formula reference: `docs/reference/current_formula_reference_ko.md`
