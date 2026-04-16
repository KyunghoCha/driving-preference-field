# Base Field 기초

이 문서는 기반 선호장(`base driving preference field`)이 무엇인지, 왜 필요한지, 그리고 현재 구현이 그 개념을 어떻게 근사하는지 설명한다. 여기서 고정하려는 것은 exact formula가 아니라 개념 모델이다. 어떤 수식을 쓰더라도 이 field가 무엇을 표현해야 하는지는 이 문서에서 분명해야 한다.

## 왜 단일 reference만으로는 부족한가

특정한 한 줄의 reference나 discrete path만으로는 이상적인 주행 흐름을 충분히 표현하기 어렵다. 지금 당장 가장 직접적인 선택이 항상 좋은 주행선을 만들지도 않는다. 이상적인 trajectory는 더 먼 progression gain 때문에 현재 약간 돌아가는 선택을 포함할 수 있다.

그래서 base field는 “어느 선을 따라갈 것인가”보다 먼저 “공간 전체에서 무엇이 더 바람직한가”를 표현해야 한다. obstacle, rule, dynamic actor 같은 예외는 이 본체와 같은 층으로 섞지 않고 분리해 다루는 편이 더 명확하다.

## base field는 무엇인가

base driving preference field는 source-agnostic semantic input을 받아 현재 질의 문맥(`QueryContext`)의 local map 전체에 대한 선호 구조를 만드는 표현이다. 입력 semantics를 라벨처럼 그대로 붙이는 것이 아니라, 그 입력을 바탕으로 어떤 상태와 trajectory가 더 바람직한지를 읽을 수 있는 공간 전체의 ordering을 만든다.

이 field의 본체는 progression-centered preference다. 공간 안에서 어디가 더 높은 preference를 가지는지, 어떤 continuation이 더 자연스러운지, 어떤 상태와 trajectory가 intended progression과 더 잘 맞는지를 progression ordering을 중심으로 설명한다. winner 결정과 최종 trajectory 형성은 상위 layer나 optimizer가 맡는다.

## progression과 drivable은 왜 분리되는가

진행 의미(`progression semantics`)와 주행 가능 의미(`drivable semantics`)는 같은 뜻이 아니다. progression은 무엇이 before이고 after인지, 어떤 흐름이 intended progression과 양립하는지를 말해 준다. drivable은 어떤 공간이 실제로 움직일 수 있는지를 말해 준다.

둘은 모두 필요하지만 서로를 대신하지는 않는다. drivable만으로는 무엇이 앞이고 뒤인지가 흐려질 수 있고, progression만으로는 지금 당장 어디를 움직일 수 있는지까지 보장하지 못한다. 그래서 base field는 둘을 한 덩어리로 섞기보다, 서로 다른 의미를 가진 입력으로 읽고 같은 공간 위에 다른 역할로 반영해야 한다.

여기서 progression은 본체 preference를 만든다. 반면 drivable은 field가 어디에서 정의될 수 있는지, local geometry를 어떻게 읽을지, progression support를 어떻게 복원하거나 보조할지를 알려 주는 입력에 가깝다. drivable을 그대로 additive preference bonus로 읽기 시작하면 “움직일 수 있음”과 “더 바람직함”이 다시 섞이게 된다.

## 이 field가 가져야 할 성질

첫째, canonical score는 `higher is better`로 읽는다. 3D surface를 뒤집어 그리거나 우물처럼 표현하는 것은 visualization 선택일 뿐, score의 의미 자체를 바꾸지는 않는다.

둘째, 이 field는 local map 전체를 덮어야 한다. reference 근처의 좁은 띠 안에서만 작동하는 구조가 아니라, 현재 보이는 local map 전체의 각 점을 progression 좌표와 transverse 좌표로 읽고 하나의 preference surface를 만들어야 한다.

셋째, progression 방향 변화와 횡방향 변화를 분리해서 다룰 수 있어야 한다. 진행축 항(`longitudinal term`)과 횡방향 항(`transverse term`)은 서로 독립적인 함수 family와 파라미터를 가질 수 있다. progression axis는 field의 주축이지, 항상 pointwise 최고점일 필요는 없다.

이 성질 때문에 같은 progression slice에서는 중심이 더 높게 보일 수 있어도, longitudinal tilt가 충분히 강하면 더 먼 progression gain이 가까운 중심 선호를 이길 수 있다. 이상적인 trajectory가 바로 앞 중심을 반드시 통과해야 할 필요는 없다는 뜻이다.

넷째, field는 ordering을 주어야지 winner direction을 미리 고르면 안 된다. split이나 merge처럼 continuation이 갈라지는 구조도 field가 branch를 “이해해서” 하나를 확정하는 대신, progression support가 여러 continuation을 만들 수 있는 구조로 남겨 두는 편이 더 자연스럽다.

## support와 gate가 secondary인 이유

progression 축과 횡방향 profile이 base field의 주성분이다. support, confidence, branch continuity, heading alignment 같은 요소는 이 구조를 돕는 보조 성분으로 머물러야 한다. 이들이 field의 본체를 대신해 nearest-reference scoring처럼 동작하면 base field는 다시 좁은 띠 기반의 점수 함수로 수축한다.

따라서 support와 gate는 ordering을 약하게 조절할 수는 있어도, field의 주축을 결정해서는 안 된다. interior boundary 같은 geometry bonus나 continuity branch 같은 continuation prior도 필요하면 보조적이거나 optional한 성분으로만 다루는 편이 맞다. field는 여전히 공간의 ordering을 알려주고, winner 결정은 상위 layer가 맡는다는 분리가 유지돼야 한다.

## 현재 구현은 이 개념을 어떻게 근사하는가

현재 구현의 progression surface는 guide마다 projection-based local coordinate를 만들고, guide-local score를 만든 뒤 hard max envelope로 합친다. Gaussian anchor는 좌표 자체를 섞는 대신 support/confidence를 만드는 약한 보조 성분으로 남긴다. exported transverse만 handoff 구간에서 부드럽게 읽고, score와 나머지 debug coordinate는 dominant guide 기준으로 유지한다.

visible guide endpoint는 semantic start/end로 읽지 않고 짧은 virtual continuation을 둔다. 목적은 endpoint 근처에 fake end-cap이 생겨 semantic meaning을 잘못 암시하는 것을 줄이는 데 있다.

구조적으로 보면 현재 progression score는 `transverse_component + longitudinal_component` 위에 `support_mod`와 `alignment_mod`가 약한 secondary modulation으로 얹히는 형태다. strong longitudinal 설정에서는 farther-ahead off-center point가 nearer-center point보다 높아질 수도 있다. exact formula는 별도 수식 문서에 정리하지만, 그 수식도 결국 이 개념 모델을 만족하는지로 읽어야 한다.

현재 tiny evaluator도 본체 score는 `progression_tilted`만 사용한다. drivable boundary는 overlay나 reconstruction 입력으로 읽고, safety / rule / dynamic burden은 costmap 성격의 시각화 채널로만 남긴다. canonical 본체를 geometry bonus나 burden 합성과 동일시하지 않는다는 점이 여기서 더 분명해진다.

## base field가 맡는 층

base field는 ideal driving preference를 담는 층이다. obstacle, dynamic actor, rule violation 같은 현실 예외를 본체에 섞기보다, 먼저 이상적 선호 구조를 정의한 뒤 예외 레이어와 분리해 조합한다.

field의 의미가 더 넓은 progression continuity와 양립한다고 해서 runtime 계산도 전역 dense map일 필요는 없다. 의미론은 더 넓은 공간 구조와 양립할 수 있고, 실제 계산은 current local map 전체를 analytic하게 평가하는 함수형 evaluator로 구현할 수 있다.

따라서 base field의 핵심은 source-agnostic progression semantics를 받아 현재 보이는 local map 전체에 대해 longitudinal term과 transverse term을 중심으로 한 선호 구조를 만들고, drivable/support 입력은 이를 지지하며, optimizer가 그 위에서 자연스러운 trajectory를 형성하게 하는 표현을 정리하는 데 있다.
