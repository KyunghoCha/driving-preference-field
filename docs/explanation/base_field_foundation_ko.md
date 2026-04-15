# Base Field 기초

이 문서는 기반 선호장(`base driving preference field`)이 무엇인지, 어떤 성질을 가져야 하는지, 그리고 현재 구현이 그 개념을 어떻게 실현하고 있는지를 설명한다. 여기서 중요한 것은 exact formula를 고정하는 일이 아니라, 이 field가 어떤 개념 모델을 따라야 하는지 분명히 하는 것이다.

출발점은 간단하다. 특정한 한 줄의 reference만으로는 이상적인 주행 흐름을 충분히 표현하기 어렵고, 지금 당장 가장 직접적인 선택이 항상 좋은 주행선을 만들지도 않는다. 이상적인 trajectory는 더 먼 progression gain 때문에 현재 약간 돌아가는 선택을 포함할 수 있다. 그래서 base field는 단일 discrete path가 아니라 공간 전체의 선호 구조를 만들어야 한다. obstacle, rule, dynamic actor 같은 예외는 이 본체와 분리해서 다뤄야 한다.

여기서 base driving preference field는 source-agnostic semantic input을 받아 현재 질의 문맥(`QueryContext`)의 local map 전체에 대해 선호 분포를 생성하는 preference structure를 뜻한다. 입력 semantics를 그대로 라벨처럼 붙이는 것이 아니라, 그 입력을 바탕으로 어떤 상태와 trajectory가 더 바람직한지를 읽을 수 있는 공간 전체의 ordering을 만든다. field는 winner direction selector가 아니라 space ordering generator이며, progression semantics와 drivable semantics는 같은 뜻이 아니다.

이 field는 몇 가지 성질을 가져야 한다. 우선 canonical score는 `higher is better`로 읽는다. 3D surface를 뒤집어 그리거나 우물처럼 표현하는 것은 visualization 선택일 뿐, score의 의미는 바뀌지 않는다. 또 field는 progression axis를 따라 점수가 어떻게 변하는지와, progression axis에서 벗어날수록 점수가 어떻게 달라지는지를 함께 가져야 한다. 진행축 항(`longitudinal term`)과 횡방향 항(`transverse term`)은 서로 독립적인 함수 family와 파라미터를 가질 수 있고, progression axis는 field의 주축이지 항상 pointwise 최고점일 필요는 없다.

가장 중요한 점은 이 field가 local map 전체를 덮는다는 사실이다. reference 근처의 좁은 띠 안에서만 작동하는 구조가 아니라, 현재 보이는 local map 전체의 각 점을 progression / longitudinal 좌표와 transverse 좌표로 읽고 하나의 preference surface를 만든다. 이때 progression semantics는 무엇이 before / after인지, 어떤 흐름이 intended progression과 양립하는지 알려주고, drivable semantics는 어떤 공간이 움직일 수 있는지 알려준다. 둘은 같이 필요하지만 같은 의미가 아니다.

같은 progression slice에서는 중심이 더 높게 보일 수 있지만, longitudinal tilt가 충분히 강하면 더 먼 progression gain이 가까운 중심 선호를 이길 수 있다. 따라서 이상적인 trajectory가 바로 앞 중심을 반드시 통과해야 할 필요는 없다. base field가 local map 전체에서 만들어야 하는 차이는 어디가 progression gain을 더 가지는지, 어디가 횡방향으로 더 자연스러운지, 어디가 더 좋은 continuation으로 이어지는지, 어디가 더 안정적인 support를 가지는지다.

support와 gate는 이 구조를 돕는 보조 성분이다. progression 축과 횡방향 profile이 주성분이고, support / confidence, branch / continuity, heading alignment 같은 요소는 field를 보조적으로 조절하는 데 머문다. 이 성분들이 nearest-reference scoring처럼 field의 본체를 대체해서는 안 된다. field는 여전히 공간의 ordering을 알려줄 뿐이며, winner 결정과 최종 trajectory 형성은 상위 layer나 optimizer가 맡는다.

현재 구현은 nearest winner가 아니라 smooth skeleton anchor를 좌표 control point로 보고 Gaussian elliptical blend로 만든 whole-fabric continuous function을 쓴다. visible guide endpoint는 semantic start/end로 해석하지 않고 짧은 virtual continuation을 둬 fake end-cap을 줄인다. branch 사이도 guide별 patch를 따로 만들지 않고 같은 함수 안에서 fabric-like surface로 메운다. exact formula는 현재 구현 수식 문서에 분리돼 있지만, 구조적으로는 `transverse_component + longitudinal_component` 위에 `support_mod`와 `alignment_mod`가 약한 secondary modulation으로 얹히는 형태다. strong longitudinal 설정에서는 farther-ahead off-center point가 nearer-center point보다 높아질 수도 있다.

이 base field는 ideal driving preference를 담는 층이다. obstacle, dynamic actor, rule violation 같은 현실 예외를 본체에 섞기보다, 먼저 이상적 선호 구조를 정의한 뒤 예외 레이어와 분리해서 조합한다. field의 의미가 더 넓은 progression continuity와 양립한다고 해서 runtime 계산도 전역 dense map일 필요는 없다. 의미론은 더 넓은 공간 구조와 양립할 수 있고, 실제 계산은 current local map 전체를 analytic하게 평가하는 함수형 evaluator로 구현할 수 있다.

따라서 base field의 핵심은 source-agnostic progression semantics를 받아 현재 보이는 local map 전체에 대해 longitudinal term, transverse term, secondary support/gate를 가진 선호 구조를 만들고, optimizer가 그 위에서 자연스러운 trajectory를 형성하게 하는 표현을 정리하는 데 있다.
