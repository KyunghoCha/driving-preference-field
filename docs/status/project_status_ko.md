# 프로젝트 진행 상태 문서

작성일: 2026-04-08

## 현재 상태

- 새 workspace 생성 완료
- docs-first 재시작 완료
- 운영 원칙 / 연구 범위 / base field 관련 canonical 문서 정리 완료
- input semantics / field terms / layer composition / runtime contract 정리 완료
- canonical progression field를 단일 source-agnostic 모델 기준으로 다시 정리 완료
- 전용 conda 환경 생성 완료
- V0 tiny analytic evaluator skeleton 추가
- toy case 기반 state / trajectory evaluator와 CLI 추가
- local raster visualization 추가
- channel별 PNG export와 composite debug view 추가
- PyQt6 기반 Parameter Lab 초기 구현 추가
- baseline/candidate compare, diff, single view 추가
- preset 저장 / load / copy와 `comparison_session.json` 기반 export 추가
- case-level ego/window control과 working context 분리 추가
- channel scale mode (`Fixed` / `Normalized`)와 range/unit 표시 추가
- Parameter Help와 summary를 current implementation guide 기준으로 정리 완료
- 단일 canonical progression field 기준으로 코드 / preset / GUI naming 정렬 완료
- current implementation을 smooth skeleton anchor blend 기반 fabric surface로 정렬 완료
- cached field runtime query layer 추가
- progression debug component view (`s_hat`, `n_hat`, longitudinal/transverse/support/alignment) 추가
- Parameter Lab profile inspection 탭과 profile export 추가
- late Phase 4 acceptance를 문서와 테스트로 고정 완료
- 현재 phase 판단은 `Phase 4 완료, Phase 5 준비 상태`

전체 phase 진행은 다음 문서에서 관리한다.

- [로드맵 문서](./roadmap_ko.md)

## 현재 합의된 것

- 외부에서 주어진 주행 가능 의미와 진행 의미를 받아 base driving preference field를 정의하는 프로젝트다
- progression field는 특정 source 예시에 종속되지 않는다
- runtime은 현재 보이는 local map 전체를 analytic하게 평가할 수 있어야 한다
- progression field는 최소한 longitudinal term과 transverse term을 가져야 하며, 이 둘은 독립적으로 조정 가능해야 한다
- current implementation은 smooth skeleton anchor를 좌표 control point로 쓰는 Gaussian-blended local-map-wide whole-fabric field를 사용한다
- current implementation exact formula는 `support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`다
- visible guide endpoint는 virtual continuation으로 처리한다
- support / alignment는 weak secondary modulation으로만 유지한다
- 자연 contour와 인공 artifact를 구분해 다룬다
- bend/U-turn의 대각선 contour와 global 등고선은 허용하고, overlap ordering flip / branch hole / fake end-cap만 제거 대상으로 본다
- support / confidence / continuity / alignment는 보조 성분이다
- canonical score는 higher is better다
- obstacle/rule/dynamic은 separate layer다
- full raster는 visualization/debugging용이다
- canonical input은 source가 아니라 semantic contract로 정의한다
- downstream consumer는 formula copy가 아니라 `field_runtime` cached query layer를 소비하는 것을 기준으로 한다

## 다음 단계

1. 이 repo에서는 Phase 4 결과를 안정 상태로 유지한다
2. morphology 미세조정은 downstream 실험 결과가 생길 때만 되돌아와 수행한다
3. runtime contract와 문서 SSOT의 drift만 계속 관리한다
4. source adapter 범위는 후속 단계로 유지한다

Phase 5 방향에 대한 현재 working proposal은 아래 reading 문서에만 남긴다.

- `docs/reading/phase5_adapter_proposal_ko.md`

## late Phase 4 acceptance lock

현재 Phase 4 종료 조건은 아래를 동시에 만족하는 것으로 본다.

- overlap 영역 ordering stability가 유지된다
- visible endpoint가 semantic start/end처럼 보이지 않는다
- `straight_corridor`, `left_bend`, `split_branch`, `merge_like_patch`, `u_turn`에서 hole / fake end-cap / abrupt ranking flip이 없다
- `FieldRuntime` public contract와 evaluator semantics가 계속 일치한다
- Parameter Lab export만으로 morphology 비교가 재현 가능하다

현재 판단:

- 위 종료 조건은 충족한 상태로 본다

이번 라운드에서 명시적으로 하지 않는 일:

- 3D preview 본체화
- source adapter
- Gazebo / RViz / MPPI hookup
- 큰 파라미터 retuning
