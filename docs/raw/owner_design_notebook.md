# Owner Design Notebook

이 문서는 현재 세션에서 게이트 직관부터 이어진 raw note를 바탕으로, 지금 시점의 사용자 설계 생각을 메타 없이 정리한 비-canonical 설계 문서다. 설계가 어떻게 형성됐는지는 별도의 `Owner Design History`에서 다루고, 이 문서는 지금 남아 있는 최신 설계 thinking만 다룬다.

## DPF가 하는 일

DPF는 입력 경로를 참고해 어디로 가는 게 더 좋은지 기울여 주는 선호장을 만드는 쪽에 가깝다. 하나의 정답 경로를 미리 고정하고 그 위를 끝까지 따라가게 만드는 장치라기보다, downstream planner가 trajectory를 고를 때 어떤 방향과 어떤 진전이 더 낫다고 볼지를 upstream에서 정리해 주는 층으로 본다.

핵심은 입력 경로를 그대로 복제하는 것이 아니라, 지금 어느 쪽이 더 나은 진전인지 읽는 기준으로 삼는 데 있다. DPF는 그 기준을 이용해 진행 선호를 표현한다.

## DPF가 하지 않는 일

DPF는 detailed path tracking을 끝까지 책임지는 planner가 아니다. 장애물 회피, 차량 동역학, 순간적인 corridor 재구성, 실제 조향과 속도 결정을 모두 여기서 끝내려고 하면 downstream planner와 역할이 겹친다.

같은 이유로 DPF가 local corridor를 지나치게 강하게 붙잡는 장치가 되는 것도 피하는 편이 맞다. 경로를 완전히 잃지 않게 방향을 주는 것과, 계속 고정시키는 것은 다른 일이다. 후자는 planner와 behavior 쪽 책임이 더 크다.

## 진행을 읽는 기준과 게이트 직관

현재 세션에서 progression을 읽는 가장 이른 직관은 기하학적 gate crossing이었다. 정상 범위 안에서 gate를 넘으면 다음으로 consume해서 넘어가고, local splice는 항상 쓰는 기본 경로가 아니라 막혔을 때만 쓰는 임시 조각이라는 생각이 먼저 나왔다.

이 직관은 progression을 “목표 노드에 충분히 가까워졌는가”보다 “지금 실제로 다음으로 넘어갈 만큼 진행했는가”로 읽게 만든다. gate 정의가 곧 DPF 수식으로 직결된다는 뜻은 아니지만, progression을 읽는 기준이 위치 도달보다 진행 방향의 통과에 더 가깝다는 문제의식은 이 문서의 출발점으로 남는다.

## 입력 경로의 역할

입력 경로는 DPF가 어디를 참고해서 progression을 읽을지 알려 주는 기준이다. 이 기준은 무시해도 되는 장식이 아니지만, 그대로 복제해야 하는 궤적도 아니다.

입력 경로가 있기 때문에 DPF는 지금 어느 쪽이 더 앞선 진전인지, reverse 같은 경우에는 어떤 방향을 progression으로 볼지를 정할 수 있다. 그러나 그 입력 경로가 곧 실제 주행 경로라는 뜻은 아니다.

## 진행방향 성분과 횡방향 성분

현재 사용자 생각에서는 진행방향 성분이 더 주역이고, 횡방향 성분은 구조를 완전히 잃지 않게 받쳐주는 쪽에 가깝다. transverse는 corridor를 완전히 놓치지 않게 하는 보조 성분이고, longitudinal는 어디로 더 가는 것이 좋은지에 대한 preference를 더 직접적으로 표현하는 성분으로 읽는다.

이렇게 보면 tuning의 목표도 달라진다. path following이 더 중요하면 transverse 비중을 높일 수 있고, 더 효율적인 진전이나 더 좋은 라인을 고르는 것이 중요하면 longitudinal 비중을 높일 수 있다. 사용자의 직관은 후자 쪽에 더 가깝다.

여기서 `Normalized` visualization은 계산 자체를 막는 것이 아니라, 화면에서 보이는 대비를 다시 펴는 역할로 본다. 따라서 longitudinal를 실제로 더 강하게 두는 것과, normalized 화면에서 그 dominance가 얼마나 선명하게 보이는지는 분리해서 읽어야 한다.

## planner / behavior와의 책임 경계

DPF는 planner와 behavior보다 앞단에서 preference를 주는 층이다. detailed path responsibility는 planner와 behavior가 더 많이 가져가야 한다. “어디로 가는 것이 더 좋은가”는 DPF가 기울여 줄 수 있지만, “지금 이 순간 어떤 steering과 speed로 그 라인을 실제로 구현할 것인가”는 downstream 쪽 문제라는 뜻이다.

이 경계가 분명해야 DPF가 centerline-following device로 과도하게 비대해지지 않는다. 반대로 DPF가 너무 약하면 planner가 참고할 진행 기준 자체가 사라진다. 따라서 역할을 없애는 것이 아니라, preference와 execution을 구분하는 것이 핵심이다.

## branch, merge, reverse를 보는 관점

branch와 merge 같은 경우에도 핵심 질문은 결국 어디로 가는 것이 더 좋은가에 가깝다. 입력 경로는 그 구조를 읽는 기준을 주되, DPF가 너무 일찍 하나의 corridor만 남기도록 수축되면 downstream planner가 선택할 여지가 줄어든다.

reverse는 별도 특수 기능이라기보다 진행방향 성분의 기울기를 반대로 두는 경우로 읽는 쪽에 더 가깝다. progression의 방향 정의가 바뀌면 같은 preference-layer 설명 안에서 다룰 수 있다는 생각이 현재 사용자 설계 생각과 더 잘 맞는다.
