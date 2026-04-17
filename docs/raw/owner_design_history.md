# Owner Design History

이 문서는 현재 세션과 확인된 gate cluster를 바탕으로, DPF 설계 생각이 어떤 문제 인식에서 시작해 어떤 전환점을 거쳐 지금의 형태에 도달했는지를 정리한 비-canonical history 문서다. 최신 설계 정리본은 `Owner Design Notebook`이 맡고, 이 문서는 그 최신 thinking이 어떤 경로를 거쳐 형성됐는지를 핵심 이정표만 따라간다.

## 문제가 처음 보인 방식

출발점은 처음부터 DPF라는 이름의 선호장을 만들겠다는 계획이 아니었다. 먼저 보인 것은 경로를 하나의 큰 덩어리로 두는 방식보다, 노드 사이 경로에 인덱스를 붙여 consume하는 방식이 더 자연스럽지 않느냐는 문제의식이었다. 여기에 더해, 당장 다음 노드로 바로 못 가더라도 갈 수 있는 길은 계속 진행해야 한다는 reachable-progress 감각이 같이 나왔다.

이 시점의 질문은 아직 longitudinal와 transverse, 선호장, canonical 수식 같은 층보다 앞에 있었다. 진행을 무엇으로 읽어야 하는가, 그리고 path를 어떤 단위로 소비하는 것이 자연스러운가가 먼저였다.

## 게이트 직관과 progression의 출발점

그 다음에 나온 더 단순한 답이 기하학적 gate crossing이었다. 주행 중에 gate를 지나면 다음 노드로 넘어간다고 읽는 편이 더 직관적이라는 생각이 먼저 서고, gate를 범위 안에서 통과한 경우에는 굳이 경로를 다시 만들지 않고 기존 흐름을 유지해야 한다는 질문이 따라붙었다.

이 전환은 progression을 `노드 근처에 충분히 도달했는가`보다 `실제로 다음으로 넘어갈 만큼 통과했는가` 쪽으로 기울게 만들었다. 이후 DPF를 다시 읽을 때도, progression의 출발 감각이 위치 도달보다 통과와 consume에 가까웠다는 점이 기준으로 남았다.

## node 도달보다 consume / 통과를 중시하게 된 흐름

gate 직관만으로 모든 경우를 덮을 수는 없었기 때문에, 진행을 읽는 기준과 막혔을 때의 재구성은 따로 보려는 흐름이 나왔다. 이때 전체 경로를 다시 만드는 대신 `ego -> current exit node`까지만 local splice를 만들고, 그 splice도 차선 범위 안에서만 허용하는 쪽이 더 맞다는 생각이 붙었다.

이 구간에서 설계는 `점 도달`보다 `segment consume` 쪽으로 더 기울었다. 정상적인 진행은 gate 통과와 segment consume으로 읽고, 길이 막혔을 때만 local splice를 제한적으로 붙이는 편이 더 자연스럽다는 감각이 여기서 자리를 잡았다.

## DPF를 progress-preference device로 읽게 된 전환

나중에 DPF 자체를 다시 정의할 때는, 이 흐름이 `경로를 끝까지 붙잡는 장치`보다 `어디로 가는 것이 더 좋은지 기울여 주는 장치`라는 framing으로 이어졌다. 입력 경로는 여전히 중요하지만, 그 선을 그대로 따라야 하는 절대 경로라기보다 지금 어느 쪽이 더 나은 진전인지 읽는 기준으로 남는다는 생각이 강해졌다.

이 전환이 나오면서 DPF는 detailed path 실행보다 진행 선호를 upstream에서 정리하는 층으로 읽히기 시작했다. 이후 설계 정리에서도 이 방향이 중심으로 남았다.

## longitudinal와 transverse에 대한 역할 재정의

progress-preference framing이 분명해지면서 longitudinal와 transverse를 보는 방식도 달라졌다. 이전보다 longitudinal가 더 주역이고, transverse는 구조를 완전히 잃지 않게 받쳐 주는 보조 성분이라는 생각이 강해졌다.

여기서 사용자의 직관은 단순히 gain을 조금 조정하자는 수준을 넘었다. path following이 더 중요하면 transverse를 강하게 둘 수 있지만, 더 좋은 진전이나 더 효율적인 라인을 고르는 것이 중요하면 longitudinal를 더 강하게 둘 수 있다는 식으로, DPF가 어떤 종류의 선호장을 만들어야 하는가를 다시 묻게 만들었다. `Normalized`는 계산을 막는 것이 아니라 화면 대비를 다시 펴는 것이라는 구분도 이 시점에 함께 분리됐다.

## planner / behavior와의 책임 경계가 분리된 과정

DPF가 진행 선호를 주는 장치라는 framing이 굳어지면서, detailed path responsibility는 planner와 behavior가 더 많이 가져가야 한다는 생각도 같이 분명해졌다. 사용자의 표현으로는, 필요한 조정은 파라미터로 만들 수 있어도 실제 path 책임까지 DPF가 다 져야 하는 것은 아니라는 쪽이었다.

이 경계는 reverse를 보는 방식에도 이어졌다. reverse를 완전히 별도 특수 모드로 분리하기보다, 진행방향 성분의 기울기를 반대로 두는 경우로 읽는 편이 더 맞다는 생각이 나왔다. progression 방향 정의를 어떻게 두느냐가 중요하다는 점이 여기서 다시 강조됐다.

## 현재 시점의 설계 위치

현재까지의 흐름을 묶으면, DPF는 segment consume과 gate 통과 직관에서 출발해, local splice와 lane range를 blocked case의 제한된 재구성으로 받아들이고, 결국에는 `어디로 가는 것이 더 좋은가`를 기울여 주는 진행 선호 장치 쪽으로 읽히고 있다. 여기에 longitudinal를 더 주역으로 보고, detailed path responsibility는 downstream planner/behavior에 더 남겨 두려는 방향이 겹쳐진다.

같은 흐름 속에서, 설계 정리 문서도 사용자 원문 anchor가 먼저 있어야 한다는 요구가 분명해졌다. 그래서 지금의 history와 latest design 문서는 raw notes를 먼저 고정한 뒤 따라가는 파생 문서로 정리되고 있다.
