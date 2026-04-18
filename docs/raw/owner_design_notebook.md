# Owner Design Notebook

이 문서는 2026-03-17 이후 raw note를 바탕으로, 지금 시점의 사용자 설계 생각을 메타 없이 정리한 비-canonical 설계 문서다. 설계가 어떻게 형성됐는지는 별도의 `Owner Design History`에서 다루고, 이 문서는 지금 남아 있는 최신 설계 thinking만 다룬다.

## DPF가 하는 일

DPF는 입력 경로와 주행 가능 의미를 참고해, 공간 안에서 어디로 가는 것이 더 좋은지 기울여 주는 선호 구조를 만드는 쪽에 가깝다. 하나의 정답 경로를 미리 고정하고 그 위를 끝까지 따라가게 만드는 장치라기보다, downstream planner가 trajectory를 고를 때 어떤 방향과 어떤 진전이 더 낫다고 볼지를 upstream에서 정리해 주는 층으로 본다.

핵심은 입력이 선호도를 직접 라벨링하는 것이 아니라, field shape 자체가 preference ordering을 만든다는 데 있다. 입력은 그 ordering을 만드는 재료이고, 선호는 구조에서 나온다.

## DPF가 하지 않는 일

DPF는 detailed path tracking을 끝까지 책임지는 planner가 아니다. 장애물 회피, 차량 동역학, 순간적인 local splice, 실제 조향과 속도 결정까지 모두 여기서 끝내려고 하면 downstream planner와 behavior의 책임을 침범하게 된다.

같은 이유로 DPF가 하나의 corridor를 강제로 붙잡는 장치가 되는 것도 피하는 편이 맞다. 경로를 완전히 잃지 않게 방향을 주는 것과, 계속 고정시키는 것은 다른 일이다. 후자는 planner와 behavior 쪽 책임이 더 크다.

## 입력 의미와 layer 분리

현재 사용자 생각에서 canonical 입력의 중심은 `주행 가능 의미`와 `진행 의미`다. base field는 이 두 축을 바탕으로 만들어지고, safety, rule, dynamic 같은 예외 요소는 base field와 같은 층이 아니라 별도의 layer로 다뤄야 한다.

이 분리는 단순 구현 편의가 아니다. base score space와 예외 burden을 같은 종류의 값으로 바로 섞으면 상쇄되면 안 되는 것들이 섞이고, 점수장의 의미도 흐려진다. 현재 framing은 base score space를 먼저 만들고, 그 위에 다른 layer를 얹는 쪽에 가깝다.

현재 latest belief에서는 raw adapter boundary도 progression guide 하나의 source shape로만 고정하지 않는다. explicit progression support가 있으면 그것을 그대로 쓰고, 없으면 global plan을 같은 directed progression support로 정규화하며, 둘 다 없을 때만 bounded drivable-only reconstruction을 시도하는 쪽이 맞다. 다만 split/merge처럼 branch topology가 ambiguous한 경우는 추측하지 않고 명시적으로 실패시키는 편이 낫다.

## 공간 전체의 점수 구조

현재 남아 있는 핵심 직관은, 점수 구조가 guide 주변의 좁은 tube support로 끝나면 안 된다는 것이다. 점수는 공간 전체에 걸쳐 정의되고, 진행방향을 따라 기울어진 ordering을 만들어야 한다. 중심 구조에서 더 멀어질수록 횡방향 profile이 낮아질 수는 있지만, 전체 object는 여전히 공간 전체의 score space여야 한다.

이 구조는 바로 앞의 local optimum만 따라가게 하기보다, 더 멀리 있는 더 좋은 진전을 ordering 안에 남겨 둘 수 있어야 한다는 직관과 연결된다. branch와 merge에서도 빈 공간이 없는 연속 surface를 더 자연스러운 목표로 본다.

## 진행을 읽는 기준과 게이트 직관

현재 세션에서 progression을 읽는 가장 이른 직관은 기하학적 gate crossing이었다. 정상 범위 안에서 gate를 넘으면 다음으로 consume해서 넘어가고, local splice는 항상 쓰는 기본 경로가 아니라 막혔을 때만 쓰는 임시 조각이라는 생각이 먼저 나왔다.

이 직관은 progression을 `목표 노드에 충분히 가까워졌는가`보다 `지금 실제로 다음으로 넘어갈 만큼 진행했는가`로 읽게 만든다. gate 정의가 곧 DPF 수식으로 직결된다는 뜻은 아니지만, progression을 읽는 기준이 위치 도달보다 통과와 consume에 더 가깝다는 문제의식은 계속 남아 있다.

## 입력 경로의 역할

입력 경로는 DPF가 어디를 참고해서 progression을 읽을지 알려 주는 기준이다. 이 기준은 무시해도 되는 장식이 아니지만, 그대로 복제해야 하는 궤적도 아니다. path piece, segment, guide, directed support 같은 표현이 계속 나오는 이유도, 입력 경로가 orientation과 ordering의 기준을 주기 때문이다.

따라서 입력 경로의 역할은 `이 선을 그대로 따라라`라기보다, `이 구조를 기준으로 지금 어느 쪽이 더 앞선 진전인지 읽어라`에 가깝다.

## 진행방향 성분과 횡방향 성분

현재 사용자 생각에서는 진행방향 성분이 더 주역이고, 횡방향 성분은 구조를 완전히 잃지 않게 받쳐주는 쪽에 가깝다. transverse는 corridor를 완전히 놓치지 않게 하는 보조 성분이고, longitudinal는 어디로 더 가는 것이 좋은지에 대한 preference를 더 직접적으로 표현하는 성분으로 읽는다.

이렇게 보면 tuning의 목표도 달라진다. path following이 더 중요하면 transverse 비중을 높일 수 있고, 더 효율적인 진전이나 더 좋은 라인을 고르는 것이 중요하면 longitudinal 비중을 높일 수 있다. 현재 사용자 직관은 후자 쪽에 더 가깝다.

현재 구현 object를 latest belief에 가장 가깝게 말하면, transverse는 dominant guide의 raw visible progression guide polyline까지의 unsigned 중심 거리에서 나오는 term이다. 이것은 signed lateral coordinate를 설명하려는 것이 아니라, 현재 progression 구조를 완전히 잃지 않게 center-high support를 주는 보조 성분으로 보는 편이 맞다.

## local evaluation과 Query Context

현재 framing에서는 local map 자체의 의미와, 그 local map을 지금 어떤 기준으로 평가하는지를 분리해서 봐야 한다. local map의 의미는 `Semantic Input Snapshot`에, 평가 시점의 pose와 window 같은 문맥은 `Query Context`에 가까운 책임이다.

이 구분 때문에 `ego_pose`, `local_window`, branch winner, support/confidence exact semantics 같은 항목은 canonical core보다 experiment나 context 쪽에 더 가깝게 남는다. field object는 공간 의미를 담고, query-time context는 그 의미를 지금 어디서 어떻게 읽는지를 정한다.

## planner / behavior와의 책임 경계

DPF는 planner와 behavior보다 앞단에서 preference를 주는 층이다. detailed path responsibility는 planner와 behavior가 더 많이 가져가야 한다. `어디로 가는 것이 더 좋은가`는 DPF가 기울여 줄 수 있지만, `지금 이 순간 어떤 steering과 speed로 그 라인을 실제로 구현할 것인가`는 downstream 쪽 문제라는 뜻이다.

이 경계가 분명해야 DPF가 centerline-following device로 과도하게 비대해지지 않는다. 반대로 DPF가 너무 약하면 planner가 참고할 progression 기준 자체가 사라진다. 따라서 역할을 없애는 것이 아니라, preference와 execution을 구분하는 것이 핵심이다.

## branch, merge, reverse를 보는 관점

branch와 merge 같은 경우에도 핵심 질문은 결국 어디로 가는 것이 더 좋은가에 가깝다. 입력 경로는 그 구조를 읽는 기준을 주되, DPF가 너무 일찍 하나의 corridor만 남기도록 수축되면 downstream planner가 선택할 여지가 줄어든다.

reverse는 완전히 별도 특수 기능이라기보다 진행방향 성분의 기울기를 반대로 두는 경우로 읽는 쪽에 더 가깝다. progression의 방향 정의가 바뀌면 같은 preference-layer 설명 안에서 다룰 수 있다는 생각이 현재 사용자 설계 생각과 더 잘 맞는다.
