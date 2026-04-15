# 연구 범위

이 문서는 `driving-preference-field`가 지금 무엇을 주장할 수 있고, 무엇은 아직 주장하지 않는지 정리한다. 목적은 설계 대화와 구현 사이의 범위 드리프트를 줄이고, 논문이나 문서에서 말할 수 있는 범위를 과장 없이 유지하는 것이다. 여기서는 프로젝트 상태가 아니라 주장 가능한 경계를 설명한다.

현재 연구 질문은 명확하다. 외부에서 주어지는 주행 가능 의미와 진행 의미를 바탕으로, 이상적인 주행 선호를 생성하는 base driving preference field를 정의할 수 있는가. 조금 더 직접적으로 말하면, 이미 주어진 semantics를 받아 공간 전체의 선호 구조를 만들고, 예외는 별도 레이어로 분리한 채 optimizer가 그 위에서 자연스러운 trajectory를 형성하게 만드는 표현 계층을 세울 수 있는가를 묻고 있다.

이 연구가 하려는 일은 path 하나를 고르는 규칙을 만드는 것이 아니다. “어떤 경로점을 따라갈 것인가”보다 “공간 안의 어떤 상태와 trajectory가 더 바람직한가”를 표현하는 구조를 정리하는 쪽에 가깝다. 따라서 핵심 결과물은 discrete route generator가 아니라, optimizer가 읽을 수 있는 whole-space preference field다.

또 이 연구는 외부 semantics를 받아 field를 생성하는 구조를 다룬다. 이 단계에서 주행 가능 공간을 perception이나 HD map processing으로 직접 추출하는 문제를 풀지는 않는다. drivable semantics와 progression semantics는 외부에서 주어진다고 가정하고, 이 입력이 어떻게 progression-centered base layer를 만들게 하는지를 다룬다.

예외를 본체와 분리하는 것도 범위에 포함된다. safety, obstacle, rule, dynamic actor는 base field와 같은 층의 개념이 아니다. 이 repo는 먼저 ideal driving preference를 담는 base layer를 정의하고, 그 위에 예외 레이어를 조합하는 구조를 전제로 한다.

여기서 drivable semantics는 본체 preference를 직접 더하는 의미라기보다, field가 정의될 공간과 progression support를 보조하거나 복원할 재료로 읽는다. branch continuity도 field가 미리 winner를 이해해서 고르는 문제가 아니라, progression support가 여러 continuation을 만들 수 있는 구조로 다루는 편이 현재 연구 질문과 맞다.

이 연구는 전역 의미와 지역 계산이 함께 필요하다는 점도 받아들인다. 개념적으로는 더 넓은 공간 구조와 양립하는 field를 상정하지만, runtime 계산이 전역 dense raster일 필요는 없다. 현재 관점은 의미론적으로는 global continuity를 유지하되, 실제 계산은 local analytic evaluation으로 수행하고 full-field raster는 설명과 디버깅을 위한 보조 표현으로 두는 쪽이다.

반대로 이 연구가 지금 하려는 것이 아닌 것도 분명하다. 이 repo는 ego에서 goal까지의 discrete path generation 자체를 제안하는 시스템이 아니다. perception이나 HD map processing으로 drivable area를 직접 추출하는 문제도 현재 범위가 아니다. full MPPI implementation, complete planner stack, vehicle dynamics-aware real-time control loop, full external stack end-to-end deployment 역시 현재 단계의 deliverable이 아니다.

geometry 보조항이나 safety burden을 어떻게 합성할지의 세부 구현도 현재 핵심 주장에 포함되지 않는다. 그런 항은 current implementation이나 downstream consumer에서 달라질 수 있으며, 본 연구가 지금 고정하려는 것은 progression-centered preference 구조와 layer split이다.

논문에서 주장 가능한 범위도 여기서 고정한다. 말할 수 있는 것은 주행 가능 의미와 진행 의미를 반영한 base field 표현의 필요성, obstacle/rule/dynamic semantics와의 레이어 분리 필요성, 그리고 샘플링 기반 최적화와 결합 가능한 표현 계층이라는 관점이다. 반대로 이 field만으로 planner 전체가 해결된다거나, 실제 차량 성능 향상을 이미 증명했다거나, lane change, split, merge, dynamic interaction 전반을 모두 해결했다고 말하는 것은 아직 과장이다.

현재 기준으로 이 연구는 외부에서 주어지는 주행 가능 의미와 진행 의미를 받아 이상적인 주행 선호를 생성하는 base driving preference field를 정의하고, 예외 요소를 별도 레이어로 분리한 채 optimizer가 그 구조를 활용하게 만드는 표현 계층을 정리하는 데 집중한다.
