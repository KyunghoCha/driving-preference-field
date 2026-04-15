# 연구 범위

`driving-preference-field`가 지금 하려는 일과 아직 하지 않으려는 일을 분명히 적어 두는 문서다. 설계 대화와 구현 사이의 범위 드리프트를 줄이고, 논문에서 주장 가능한 범위를 과장 없이 유지하는 것이 목적이다.

현재 연구 질문은 명확하다. 외부에서 주어지는 주행 가능 의미와 진행 의미를 바탕으로, 이상적인 주행 선호를 생성하는 base driving preference field를 정의할 수 있는가. 조금 더 풀어 쓰면, 주행 가능 의미가 이미 주어졌다고 할 때 공간 전체의 선호 구조를 만들고, 장애물이나 규칙 같은 예외는 별도 레이어로 다루며, optimizer가 그 위에서 자연스럽게 trajectory를 만들게 하는 표현을 세울 수 있는가를 묻고 있다.

이 연구가 하려는 일은 세 가지다. 첫째, “어떤 경로점을 따라갈 것인가”보다 “공간 내 어떤 상태와 trajectory가 더 바람직한가”를 표현하는 방식을 정리한다. 둘째, 외부 semantics를 받아 field를 생성하는 구조를 다룬다. 이 단계에서 주행 가능 공간을 직접 추출하는 문제를 풀려는 것은 아니고, drivable semantics와 progression semantics가 주어졌다고 가정한다. 셋째, base field와 safety / obstacle / rule / dynamic 같은 예외 레이어를 같은 층으로 취급하지 않는다.

이 연구가 전역 의미와 지역 계산을 함께 다룬다는 점도 범위에 포함된다. field는 개념적으로는 더 넓은 공간 구조와 양립할 수 있지만, runtime 계산은 전역 dense raster일 필요가 없다. 현재 관점은 의미론적으로는 global field를 상정하면서도 runtime에서는 local analytic evaluation을 사용하고, full-field raster는 설명과 디버깅을 위한 보조 표현으로 두는 쪽이다.

반대로 이 연구가 지금 하려는 것이 아닌 것도 분명하다. 이 repo는 ego에서 goal까지의 discrete path generation 자체를 제안하는 시스템이 아니다. perception이나 HD map processing으로 drivable area를 직접 추출하는 문제도 현재 범위가 아니다. full MPPI implementation, complete planner stack, vehicle dynamics-aware real-time control loop, full external stack end-to-end deployment 역시 현재 단계의 deliverable이 아니다. base field와 obstacle layer를 단순 합으로만 해석하는 것도 현재 목표가 아니다.

논문에서 주장 가능한 범위도 여기서 같이 고정한다. 주장할 수 있는 것은 주행 가능 의미와 진행 의미를 반영한 base field 표현의 필요성, obstacle / rule / dynamic semantics와의 레이어 분리 필요성, 그리고 샘플링 기반 최적화와 결합 가능한 표현 계층이라는 관점이다. 반대로 이 field만으로 planner 전체가 해결된다거나, 실제 차량 성능 향상을 이미 증명했다거나, lane change / split / merge / dynamic interaction 전반을 모두 해결했다고 말하는 것은 아직 과장이다.

현재 기준으로 이 연구는 외부에서 주어지는 주행 가능 의미와 진행 의미를 받아 이상적인 주행 선호를 생성하는 base driving preference field를 정의하고, 예외 요소를 별도 레이어로 분리한 채 optimizer가 그 구조를 활용하게 만드는 표현 계층을 정리하는 데 집중한다.
