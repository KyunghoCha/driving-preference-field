# 프로젝트 개요

`driving-preference-field`는 왜 필요한가, 무엇을 만들고 있는가, 그리고 지금 어디까지 왔는가를 설명하는 문서다. 이 repo는 진행 의미(`progression semantics`)와 주행 가능 의미(`drivable semantics`)를 받아 현재 보이는 local map 전체에 대한 driving preference를 정의하고 실험한다. 여기서 말하는 field는 구현 편의용 점수 raster가 아니라, local map을 어떻게 읽어야 하는지에 대한 개념 모델이다.

단일 reference path만으로는 이상적인 주행 흐름을 충분히 설명하기 어렵다. 지금 가장 가까운 중심이나 가장 직접적인 선택이 항상 좋은 trajectory를 만들지는 않는다. planner나 optimizer가 자연스러운 trajectory를 만들게 하려면, discrete route보다 먼저 공간 전체의 선호 구조가 필요하다.

이 프로젝트가 만드는 것은 path scorer가 아니라 공간 전체 선호장(`whole-space preference field`)이다. 특정 선을 따라가라고 지시하는 대신, 지금 보이는 공간에서 어떤 상태와 trajectory가 더 바람직한지를 ordering으로 읽게 한다. 입력이 source-specific하더라도 그 형태를 바로 truth로 올리지 않고, 의미 계약(`semantic contract`)을 거쳐 같은 종류의 공간 구조로 번역해 다룬다.

여기서 핵심은 진행 의미와 주행 가능 의미를 분리하는 것이다. 주행 가능 의미는 지금 움직일 수 있는 공간을 말해 주지만, 무엇이 앞이고 뒤인지까지 보존하지는 못할 수 있다. 진행 의미는 intended progression과 양립하는 흐름과 before/after ordering을 만들지만, 실제로 지금 어디를 움직일 수 있는지를 대신 보장하지는 않는다.

이 분리는 “움직일 수 있음”과 “어떤 흐름이 더 자연스러운가”가 같은 질문이 아니라는 판단에서 출발한다. local drivable support가 progression support를 조금 벗어나더라도 주행 의미 자체는 곧바로 사라지지 않아야 한다. 반대로 progression support가 있다고 해서 그 주변이 모두 지금 당장 움직일 수 있는 공간이 되는 것도 아니다.

이 프로젝트에서 progression은 단순한 ego heading이나 centerline 방향이 아니다. 직선에서는 무엇이 앞으로 이어지는지, bend와 split에서는 어떤 continuation이 progression과 양립하는지, 그리고 이 local place에서 무엇이 before이고 after인지 정해 주는 ordering이다. 즉 progression은 winner direction을 미리 고르는 discrete action이 아니라, local map 전체에 진행축과 횡방향 구조를 만드는 의미다.

field의 역할도 여기서 정해진다. field는 같은 progression slice에서 중심이 더 나은지, 더 먼 progression gain이 가까운 중심 선호를 언제 이길 수 있는지, branch나 continuity ambiguity가 어떤 spatial ordering을 만드는지를 알려 준다. 반면 실제 방향 선택, winner 결정, control command는 상위 layer나 optimizer가 맡는다. field는 공간을 설명하지, 행동을 직접 결정하지 않는다.

따라서 모든 contour를 없애는 것이 목표는 아니다. bend나 U-turn에서 생기는 대각선 contour, 2D heatmap에서 비틀린 면처럼 보이는 global 등고선은 허용할 수 있다. 제거 대상은 overlap 영역 ordering flip, branch 사이 hole, visible endpoint가 semantic start/end처럼 보이는 fake end-cap, active-set이나 neighborhood 처리 때문에 생기는 abrupt jump 같은 구현 artifact다.

SSC는 이 아이디어를 실제로 검증하는 중요한 downstream validation source다. 하지만 SSC가 canonical truth는 아니다. SSC에서 얻은 요구사항과 관찰은 evidence로만 받아들이고, 이 repo는 끝까지 source-agnostic field와 contract를 정의하는 기준점으로 남는다.

현재 이 repo는 `Phase 5 완료, Phase 6 준비 상태`다. canonical 문서, toy case와 evaluator, local raster visualization, Parameter Lab compare workflow, cached runtime query layer, generic source adapter SSOT와 reference adapter, debug component view와 profile inspection, semantic-first acceptance lock까지 정리돼 있다. Gazebo, RViz, MPPI hookup과 optimizer integration은 이 repo의 범위가 아니다.

한 문장으로 정리하면, `driving-preference-field`는 progression semantics와 drivable semantics를 받아 현재 보이는 local map 전체에 대한 whole-space preference field를 정의하고, 그 field가 공간의 ordering을 알려 주며 실제 방향 선택은 상위 layer가 맡게 만드는 프로젝트다.
