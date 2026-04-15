# 프로젝트 개요

`driving-preference-field`는 진행 의미(`progression semantics`)와 주행 가능 의미(`drivable semantics`)를 받아, 현재 보이는 local map 전체에 대한 driving preference를 정의하고 실험하는 연구 워크스페이스다. 이 문서는 왜 이런 field가 필요한지, 무엇을 만들고 있는지, 그리고 이 repo가 현재 어디까지 와 있는지를 한 번에 설명한다.

단일 reference path만으로는 이상적인 주행 흐름을 충분히 표현하기 어렵다. 지금 당장 가장 가까운 중심이나 가장 직접적인 선택이 항상 좋은 trajectory를 만들지도 않는다. 장애물, 규칙, 동적 객체 같은 현실 예외와 이상적인 주행 선호도는 같은 층이 아니고, planner나 optimizer가 자연스럽게 trajectory를 만들려면 discrete route보다 먼저 공간 전체의 선호 구조가 필요하다. 이 프로젝트는 바로 그 선호 구조를 정의하는 쪽을 택한다.

이 repo의 본체는 path scorer가 아니라 공간 전체 선호장(`whole-space preference field`)이다. source-specific 입력을 직접 truth로 올리지 않고, 의미 계약(`semantic contract`)을 받아 local map 전체의 상태와 trajectory를 ordering으로 읽게 하는 preference structure를 만든다. 즉 중심은 “어떤 선을 따라가라”가 아니라 “지금 보이는 공간에서 어디가 더 바람직한가”다.

이때 핵심은 progression과 drivable을 분리해서 보는 것이다. 주행 가능 의미는 지금 움직일 수 있는 공간을 알려주지만, 무엇이 앞이고 뒤인지 자체를 보존하지 못할 수 있다. 진행 의미는 반대로 intended progression과 양립하는 흐름, 그리고 before/after ordering을 주지만, 실제로 지금 어디를 움직일 수 있는지까지 대신 말해주지는 않는다. local drivable support가 progression support를 조금 벗어나더라도 주행 의미 자체는 곧바로 사라지지 않아야 한다는 점이 이 분리의 출발점이다.

이 프로젝트에서 progression은 단순한 ego heading이나 centerline 방향이 아니다. 그것은 이 local place에서 무엇이 before이고 무엇이 after인지, 직선에서는 어떤 흐름이 앞으로 이어지고 bend나 split에서는 어떤 continuation이 progression과 양립하는지를 정해 주는 ordering이다. progression은 winner 방향을 강제하는 discrete action이 아니라, local map 전체에 진행축(`longitudinal`) / 횡방향(`transverse`) 구조를 만들게 하는 의미다.

field의 역할도 여기서 분명해진다. field는 어떤 영역이 더 높은 preference를 가지는지, 같은 progression slice에서 중심이 더 좋은지, 더 먼 progression gain이 가까운 중심 선호를 언제 이길 수 있는지, branch나 continuity ambiguity가 어떤 spatial ordering을 만드는지를 알려 준다. 반면 실제 방향 선택, winner 결정, control command는 상위 layer나 optimizer가 담당한다. 이 field는 공간을 설명하지, 행동을 직접 결정하지 않는다.

모든 contour를 없애는 것도 목표가 아니다. bend나 U-turn에서 보이는 대각선 contour, 2D heatmap에서 비틀린 면처럼 보이는 global 등고선은 허용할 수 있다. 대신 overlap 영역 ordering flip, branch 사이 hole, visible endpoint가 semantic start/end처럼 보이는 fake end-cap, active-set이나 neighborhood 처리 때문에 생기는 abrupt jump 같은 구현 artifact는 제거 대상이다. 기준은 그림이 단순한지 복잡한지가 아니라, 공간 기하에서 자연스럽게 나온 구조인지 구현 artifact인지다.

SSC는 이 아이디어를 실제로 검증하는 중요한 downstream validation source다. 하지만 SSC가 canonical truth는 아니다. SSC에서 나온 요구사항은 evidence로만 받아들이고, 이 repo는 끝까지 점수장 SSOT를 유지한다. downstream 환경이 무엇이든, 이 repo는 source-agnostic field와 contract를 정의하는 기준점이어야 한다.

현재 이 repo는 `Phase 5 완료, Phase 6 준비 상태`다. canonical 문서, tiny evaluator와 toy case, local raster visualization, Parameter Lab compare workflow, cached runtime query layer, generic source adapter SSOT와 reference adapter, debug component view와 profile inspection, semantic-first acceptance lock까지 정리돼 있다. 반면 Gazebo / RViz / MPPI hookup이나 optimizer integration은 이 repo의 범위가 아니다.

한 문장으로 정리하면, `driving-preference-field`는 progression semantics와 drivable semantics를 받아 현재 보이는 local map 전체에 대해 whole-space preference field를 정의하고, 그 field는 공간의 ordering을 알려주며 실제 방향 선택은 상위 layer가 하게 만드는 프로젝트다.
