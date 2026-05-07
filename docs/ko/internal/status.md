# 내부 상태

## 프로젝트 상태

- canonical 문서와 코드는 source-agnostic progression field라는 한 줄기 위에서 다시 정렬돼 있다.
- `Phase 5 완료, Phase 6 준비 상태`는 여전히 유지한다.
- tiny evaluator, toy case, generic adapter fixture, raster visualization, cached runtime query, Parameter Lab GUI가 있다.
- 이 repo는 여전히 score-field SSOT이지, integration workspace는 아니다.

## 현재 truth

지금 이 프로젝트가 구현하지 않는 것은 다음과 같다.

- planner
- controller
- full MPPI stack
- interactive geometry editor
- Gazebo / RViz hookup

지금 이 프로젝트가 정의하고 있는 것은 다음과 같다.

- reference-path cost model가 무엇인지
- local-map-wide progression-aware field를 어떻게 설명하는지
- longitudinal / transverse를 독립 축으로 어떻게 다루는지
- support, confidence, continuity, alignment를 어떻게 약한 secondary modulation으로 남기는지
- exception layer를 reference-path cost model와 분리해서 어떻게 읽는지
- runtime local evaluation을 어떻게 해석하는지
- config-driven comparison과 preset-based experiment가 lab 안에서 어떻게 동작해야 하는지
- 현재 truth를 downstream 세부사항 없이 문서가 어떻게 설명하는지
- generic external-like source를 canonical snapshot/context contract로 어떻게 번역하는지

## 현재 집중점

- Phase 5 결과를 SSOT로 안정적으로 유지한다.
- morphology retuning은 open-ended redesign이 아니라 downstream evidence가 있을 때만 움직인다.
- 고정된 adapter contract는 design SSOT에 두고, proposal/history는 reading 문서에 남긴다.
- SSC나 다른 downstream 환경이 canonical truth로 승격되지 않게 계속 막는다.

## 정리 경계

- canonical 문서와 코드는 single-field naming 위에서 맞춰져 있다.
- 오래된 experimental naming은 active code, preset, test에서 제거됐다.
- 남은 일은 version cleanup이 아니라 SSOT 안정화, 문서 가독성, 이후 downstream 준비다.
