# 프로젝트 개요

이 문서는 `driving-preference-field`가 왜 필요한지, 무엇을 만들고 있는지, 지금 어디까지 왔는지 설명한다. 여기서 먼저 고정할 질문은 하나다. 이 repo가 discrete path를 고르는 도구인지, 아니면 local map 전체의 선호 구조를 정의하는 도구인지다.

이 프로젝트는 path scorer가 아니라 공간 전체 선호장(`whole-space preference field`)을 다룬다. 특정 선을 따라가라고 지시하는 대신, 지금 보이는 local map에서 어떤 상태와 trajectory가 더 바람직한지를 ordering으로 읽게 한다. 이 field는 행동을 직접 결정하지 않고, 상위 layer나 optimizer가 자연스러운 trajectory를 만들 수 있게 기준면을 제공한다.

단일 reference path만으로는 이상적인 주행 흐름을 충분히 설명하기 어렵다. 지금 가장 가까운 중심이나 가장 직접적인 선택이 항상 좋은 trajectory를 만들지는 않는다. planner가 더 자연스러운 선택을 하게 하려면, discrete route보다 먼저 공간 전체에 대한 선호 구조가 있어야 한다.

이 repo가 progression semantics를 중심에 두는 이유도 여기에 있다. progression은 단순한 heading이 아니라, 이 local place에서 무엇이 before이고 after인지, 어떤 continuation이 intended progression과 양립하는지를 정해 주는 ordering이다. 반면 drivable semantics는 지금 어디가 움직일 수 있는 공간인지를 알려 준다.

진행 의미와 주행 가능 의미는 같은 질문이 아니다. drivable만으로는 무엇이 앞이고 뒤인지가 흐려질 수 있고, progression만으로는 지금 당장 어디를 움직일 수 있는지를 보장하지 못한다. 그래서 이 repo는 둘을 섞어 하나의 보너스 점수로 처리하기보다, progression은 본체 preference를 만들고 drivable은 domain, support, reconstruction 입력으로 읽는 쪽을 택한다.

이 판단은 branch와 obstacle을 다루는 방식도 같이 결정한다. branch는 field가 미리 winner를 정하는 대상이 아니다. progression support가 여러 continuation을 만들 수 있는 구조로 읽는 편이 이 프로젝트의 철학과 맞다. obstacle, rule, dynamic actor는 base field와 같은 층의 개념이 아니므로, ideal preference를 담는 본체와 별도 레이어로 분리해 다룬다.

현재 runtime은 이 철학을 향한 현재 구현을 포함한다. 본체 score는 `progression_tilted`를 중심으로 읽고, drivable boundary는 overlay/support로 다룬다. obstacle / rule / dynamic은 costmap 성격의 시각화와 burden layer로 분리돼 있다. 즉 canonical 철학과 현재 구현은 최대한 맞춰 두되, 구현 디테일과 본체 개념을 같은 것으로 취급하지는 않는다.

SSC는 이 아이디어를 실제로 검증하는 중요한 downstream validation source다. 하지만 SSC가 canonical truth는 아니다. SSC에서 얻은 요구사항과 관찰은 evidence로 읽고, 이 repo는 끝까지 source-agnostic field와 contract를 정의하는 기준점으로 남는다.

현재 이 repo는 `Phase 5 완료, Phase 6 준비 상태`다. canonical 문서, toy case와 evaluator, local raster visualization, Parameter Lab compare workflow, cached runtime query layer, generic source adapter SSOT와 reference adapter, debug component view와 profile inspection, semantic-first acceptance lock까지 정리돼 있다. Gazebo, RViz, MPPI hookup과 optimizer integration은 이 repo의 범위가 아니다.

한 문장으로 요약하면, `driving-preference-field`는 progression semantics와 drivable semantics를 받아 현재 보이는 local map 전체에 대한 whole-space preference field를 정의하고, 그 ordering을 optimizer가 읽게 만드는 프로젝트다.
