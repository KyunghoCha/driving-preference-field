# Owner Design History

이 문서는 현재 세션과 확인된 gate cluster를 바탕으로, DPF 설계 생각이 어떤 문제 인식에서 시작해 어떤 전환점을 거쳐 지금의 형태에 도달했는지를 정리한 비-canonical history 문서다. 최신 설계 정리본은 `Owner Design Notebook`이 맡고, 이 문서는 그 최신 thinking이 어떤 경로를 거쳐 형성됐는지를 핵심 이정표만 따라간다.

## 문제가 처음 보인 방식

출발점은 처음부터 `DPF`라는 이름의 선호장을 만들겠다는 계획이 아니었다. 먼저 보인 것은 진행을 어떻게 읽어야 하느냐는 문제였다. 노드 근처에 충분히 접근했는지, 거리 기반 arm 조건을 만족했는지 같은 판정은 상황을 설명하기보다 예외를 더 만드는 것처럼 보였고, 실제로 다음으로 넘어갔다고 볼 수 있는 더 직접적인 기준이 필요하다는 감각이 먼저 나왔다.

이 시점의 문제 인식은 아직 whole-space field나 longitudinal/transverse 같은 항 분해보다 앞에 있었다. 질문은 수식이 아니라, 무엇을 progression이라고 읽어야 자연스러운가였다.

## 게이트 직관과 progression의 출발점

그 첫 답이 기하학적 gate crossing이었다. 주행 중에 게이트를 지나면 다음 노드나 다음 segment로 넘어간다고 읽는 편이 더 단순하고 자연스럽다는 직관이 먼저 섰다. gate를 정상 범위 안에서 통과했다면 굳이 경로를 다시 만들지 말고 그대로 consume하고 넘어가면 되고, local splice는 기본 동작이 아니라 막혔을 때만 쓰는 임시 조각으로 밀어내는 편이 더 맞는다고 봤다.

이 전환은 progression을 “목표 위치에 도달했는가”에서 “실제로 다음으로 넘어갈 만큼 통과했는가”로 바꿨다. 나중에 DPF를 설명할 때도 중요한 것은 이 gate를 수식으로 그대로 복제하는지가 아니라, progression의 출발 감각이 위치 도달보다 통과와 consume에 더 가까웠다는 점이다.

## node 도달보다 consume / 통과를 중시하게 된 흐름

gate 직관이 자리 잡으면서 node consumption보다 segment consumption이 더 자연스럽다는 생각이 같이 강해졌다. 진행은 개별 점을 찍는 사건이라기보다, 구조를 따라 다음 부분으로 넘어가는 사건으로 읽혀야 한다는 쪽으로 무게가 옮겨갔다.

여기서 local splice의 역할도 다시 정리됐다. splice는 기본 경로 흐름이 아니라, 정상적인 gate 통과가 막힐 때만 쓰는 예외적 fallback이어야 했다. 이 구분은 나중에 branch나 merge를 볼 때도 영향을 남겼다. 정상적인 progression을 읽는 기준과, 막혔을 때 임시로 이어 붙이는 조각을 같은 층에서 설명하면 설계가 금방 흐려진다는 감각이 이 시점에 생겼다.

## DPF를 progress-preference device로 읽게 된 전환

그 다음 큰 전환은 DPF가 “경로를 끝까지 붙잡는 장치”가 아니라 “어디로 가는 것이 더 좋은지 기울여 주는 장치”라는 framing이 분명해진 것이다. 입력 경로는 여전히 중요하지만, 그것이 실제로 복제해야 하는 궤적이라는 생각에서 벗어나기 시작했다. 입력 경로는 progression과 branch ordering을 읽기 위한 reference spine이고, DPF는 그 spine을 참고해 whole-space preference를 만드는 층이라는 해석이 점점 선명해졌다.

이 전환 덕분에 planner와 behavior가 가져가야 할 책임도 분리되기 시작했다. DPF가 trajectory를 확정하는 planner가 되면 downstream과 역할이 겹치고, 반대로 아무 기준도 주지 못하면 planner가 참고할 preference spine이 사라진다. 그래서 DPF는 detailed execution보다 progression-centered preference를 주는 쪽으로 자리를 잡게 됐다.

## longitudinal와 transverse에 대한 역할 재정의

progress-preference framing이 분명해지면서 longitudinal와 transverse를 보는 방식도 바뀌었다. 이전에는 transverse가 경로와 corridor를 붙잡는 중심 성분처럼 읽히기 쉬웠지만, 나중에는 longitudinal가 더 주역이고 transverse는 구조를 완전히 잃지 않게 받쳐 주는 보조 성분이라는 생각이 강해졌다.

이 변화는 단순한 gain 조정 아이디어로 끝나지 않았다. path following이 더 중요하면 transverse를 더 강하게 둘 수 있고, 더 좋은 진전이나 더 효율적인 라인을 고르는 것이 중요하면 longitudinal를 더 강하게 둘 수 있다는 관점이 나오면서, 이 문제는 tuning이라기보다 DPF가 어떤 종류의 preference field여야 하는가를 묻는 문제로 옮겨갔다.

여기서 `Normalized` visualization도 다시 분리됐다. normalized는 화면 대비를 다시 펴는 도구이지, 계산에서 longitudinal dominance 자체를 막는 장치가 아니라는 구분이 생겼다. 이 역시 수식보다 역할 정의를 먼저 다시 읽게 만든 전환점이었다.

## planner / behavior와의 책임 경계가 분리된 과정

DPF가 진행 선호를 주는 장치라는 framing이 나오면서, planner / behavior와의 책임 경계도 더 분명해졌다. detailed path tracking, 실제 steering과 speed 결정, 순간적인 corridor 재구성은 downstream이 더 많이 가져가야 하는 일로 읽혔다. DPF는 어느 방향과 어떤 진전이 더 좋은지를 bias로 제공하지만, 그 bias를 실제 trajectory와 control로 구현하는 것은 planner / behavior 쪽 책임이라는 구분이다.

이 경계는 reverse를 보는 방식에도 영향을 주었다. reverse는 완전히 별도의 특수 모드라기보다, 진행방향 성분의 기울기를 반대로 두는 경우로 읽는 편이 더 맞다는 생각이 나왔다. progression의 방향 정의만 바뀌면 같은 preference-layer 설명 안에 reverse도 넣을 수 있다는 관점이다.

## 현재 시점의 설계 위치

현재까지의 흐름을 묶으면, DPF는 입력 경로를 reference spine으로 사용해 progression과 branch ordering을 읽고, 그 결과를 whole-space preference로 펼치는 장치 쪽으로 정리되고 있다. 설계의 출발점은 gate crossing과 consume intuition이었고, 그 위에서 progress-preference framing, longitudinal 중심 직관, downstream responsibility 분리가 차례로 얹혔다.

아직 이 생각이 canonical truth로 고정된 것은 아니다. 다만 지금 시점에서 분명한 것은 DPF를 centerline-following device로 키우는 것보다, progression-centered preference layer로 읽는 편이 현재까지의 문제 인식과 발전 과정에 더 잘 맞는다는 점이다.
