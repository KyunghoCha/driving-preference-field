# 진행 상태

현재 repo는 **Phase 5 완료, Phase 6 준비 상태**다. 아래는 지금까지 끝난 일, 현재 유지하고 있는 합의, 그리고 다음 단계에서 이 repo가 무엇을 할지에 대한 짧은 상태 기록이다.

## 완료

- 새 workspace 생성
- docs-first 재시작
- 운영 원칙 / 연구 범위 / base field 관련 canonical 문서 정리
- input semantics / field terms / layer composition / runtime contract 정리
- canonical progression field를 단일 source-agnostic 모델 기준으로 다시 정리
- 전용 conda 환경 생성
- tiny analytic evaluator skeleton 추가
- toy case 기반 state / trajectory evaluator와 CLI 추가
- local raster visualization 추가
- channel별 PNG export와 composite debug view 추가
- PyQt6 기반 Parameter Lab 초기 구현 추가
- baseline/candidate compare, diff, single view 추가
- preset 저장 / load / copy와 `comparison_session.json` 기반 export 추가
- case-level ego/window control과 working context 분리 추가
- channel scale mode (`Fixed` / `Normalized`)와 range/unit 표시 추가
- Parameter Help와 summary 정리
- pooled blended progression coordinate field 현재 구현 정리
- cached field runtime query layer 추가
- public batched progression runtime query 추가
- progression debug component view 추가
- Parameter Lab profile inspection 탭과 profile export 추가
- late Phase 4 acceptance를 문서와 테스트로 고정
- generic source adapter SSOT 문서 추가
- generic YAML/JSON reference adapter와 fixtures 추가
- adapter inspection / conversion CLI 추가
- toy path와 generic adapter path를 병행 유지하도록 loader dispatch 추가
- Parameter Lab이 generic adapter input path도 직접 열 수 있게 정리

전체 phase 진행은 [로드맵 문서](./roadmap.md)에서 관리한다.

## 현재 합의

- 외부에서 주어진 주행 가능 의미와 진행 의미를 받아 base driving preference field를 정의하는 프로젝트다.
- progression field는 특정 source 예시에 종속되지 않는다.
- runtime은 현재 보이는 local map 전체를 analytic하게 평가할 수 있어야 한다.
- progression field는 최소한 longitudinal term과 transverse term을 가져야 하며, 이 둘은 독립적으로 조정 가능해야 한다.
- 현재 구현은 soft progress gating을 둔 pooled blended progression field를 사용하고, transverse는 가장 가까운 resampled progression guide segment에 직접 투영해 읽는다.
- 현재 구현 exact formula는 `support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`다.
- visible guide endpoint는 virtual continuation으로 처리한다.
- support / alignment는 weak secondary modulation으로만 유지한다.
- current base composition은 `progression_tilted`만 사용한다.
- safety / rule / dynamic burden은 costmap 성격의 visualization 채널로만 유지한다.
- 자연 contour와 인공 artifact를 구분해 다룬다.
- bend/U-turn의 대각선 contour와 global 등고선은 허용하고, overlap ordering flip / branch hole / fake end-cap만 제거 대상으로 본다.
- support / confidence / continuity / alignment는 보조 성분이다.
- canonical score는 higher is better다.
- obstacle/rule/dynamic은 separate layer다.
- full raster는 visualization/debugging용이다.
- canonical input은 source가 아니라 semantic contract로 정의한다.
- raw source가 아니라 adapter output contract가 canonical이다.
- downstream consumer는 formula copy가 아니라 `field_runtime` cached query layer를 소비하는 것을 기준으로 한다.
- batched progression query는 `query_state` / `query_trajectory`와 의미상 일치하는 public contract로 본다.
- adapter는 의미 번역기만 하며 branch winner를 정하지 않는다.
- `ego_pose`는 snapshot 본체가 아니라 `QueryContext` 책임으로 둔다.
- `local_window` 정책은 canonical truth가 아니라 experiment 영역으로 남긴다.
- support/confidence/branch prior는 optional weak prior로만 다룬다.

## 현재 focus

1. 이 repo에서는 Phase 5 결과를 안정 상태로 유지한다.
2. morphology 미세조정은 downstream 실험 결과가 생길 때만 되돌아와 수행한다.
3. runtime contract와 adapter contract, 문서 SSOT의 drift만 계속 관리한다.
4. integration 요구사항은 downstream evidence로만 받아 다시 canonical로 승격할지 판단한다.

현재 source adapter의 design SSOT는 `docs/ko/reference/source_adapter.md`에 있고, proposal history는 `docs/ko/reading/history/phase5_adapter_proposal.md`에 남긴다.

## Phase 4 종료 기준

현재 Phase 4 종료 조건은 아래를 동시에 만족하는 것으로 본다.

- overlap 영역 ordering stability가 유지된다.
- visible endpoint가 semantic start/end처럼 보이지 않는다.
- `straight_corridor`, `left_bend`, `split_branch`, `merge_like_patch`, `u_turn`에서 hole / fake end-cap / abrupt ranking flip이 없다.
- `FieldRuntime` public contract와 evaluator semantics가 계속 일치한다.
- Parameter Lab export만으로 morphology 비교가 재현 가능하다.

현재 판단은 위 종료 조건을 충족한 상태다.

## 비범위

- 3D preview 본체화
- Gazebo / RViz / MPPI hookup
- 큰 파라미터 retuning
