# Owner Design History

이 문서는 2026-03-17 이후 materialized session source와 현재 active thread를 바탕으로, DPF 설계 생각이 어떤 문제 인식에서 시작해 어떤 전환점을 거쳐 지금의 형태에 도달했는지를 정리한 비-canonical history 문서다. 최신 설계 정리본은 `Owner Design Notebook`이 맡고, 이 문서는 그 최신 thinking이 어떤 경로를 거쳐 형성됐는지를 핵심 전환점 기준으로 따라간다.

## 문제가 처음 보인 방식

출발점은 처음부터 DPF라는 이름의 선호장을 만들겠다는 계획이 아니었다. 먼저 보인 것은 경로를 하나의 큰 객체로 유지하는 방식보다, 노드 사이 path piece에 인덱스를 붙여 consume하는 쪽이 더 자연스럽지 않느냐는 문제의식이었다. 여기에 더해, 당장 다음 노드로 못 가더라도 갈 수 있는 길은 계속 진행해야 한다는 reachable-progress 감각이 같이 나왔다.

이 시점의 질문은 아직 수식이나 점수장보다 앞에 있었다. 진행을 무엇으로 읽어야 하는가, 그리고 path를 어떤 단위로 소비하는 것이 자연스러운가가 먼저였다. 이후 DPF가 progression을 읽는 방식도 이 초기 감각의 연장선 위에서 다시 해석되기 시작했다.

## 게이트 직관과 progression의 출발점

그 다음에 나온 더 단순한 답이 기하학적 gate crossing이었다. 주행 중에 gate를 지나면 다음 노드로 넘어간다고 읽는 편이 더 직관적이라는 생각이 먼저 서고, gate를 범위 안에서 통과한 경우에는 굳이 경로를 다시 만들지 않고 기존 흐름을 유지해야 한다는 질문이 따라붙었다.

이 전환은 progression을 `목표 노드 근처에 충분히 왔는가`보다 `실제로 다음으로 넘어갈 만큼 통과했는가` 쪽으로 기울게 만들었다. 이후 DPF를 다시 읽을 때도, progression의 출발 감각이 위치 도달보다 통과와 consume에 가까웠다는 점이 기준으로 남았다.

## node 도달보다 consume / 통과를 중시하게 된 흐름

gate 직관만으로 모든 경우를 덮을 수는 없었기 때문에, 정상적인 consume와 blocked 상황의 재구성을 분리해서 보려는 흐름이 나왔다. 이때 전체 경로를 다시 만드는 대신 `ego -> next`까지만 local splice를 만들고, 그 splice도 차선 범위 안에서만 허용하는 쪽이 더 맞다는 생각이 붙었다.

여기서 중요한 건, local splice가 기본 progression rule이 아니라는 점이었다. 정상적인 진행은 gate 통과와 segment consume으로 읽고, 길이 막혔을 때만 local splice를 제한적으로 붙이는 편이 더 자연스럽다는 감각이 자리를 잡기 시작했다.

## gate-only 단순화가 흔들린 과정

3월 22일 무렵에는 gate-only 단순화가 실제 blocked progression 앞에서 흔들리기 시작했다. `못 가면 그냥 멈춘다`가 아니라, 장애물이 current/next node를 막더라도 갈 수 있는 frontier까지는 계속 전진해야 하지 않느냐는 pressure가 explicit하게 올라왔다. 이때 `행동이 경로를 못 잡아주는 것 아니냐`, `못 가면 갈 수 있는 곳까지 플래닝하는 것이 맞지 않느냐`는 질문이 같이 나왔다.

이 전환으로 인해 progression은 `segment consume`과 `frontier 전진`을 함께 생각해야 하는 문제가 되었다. gate crossing만으로 progression을 다 설명하려는 시도는 약해졌고, blocked case에서는 frontier/local splice가 먼저 움직이고 consume는 나중에 일어나야 한다는 구분이 더 선명해졌다. 이후 설계 역사에서 남은 것은, progression을 읽는 기준이 단순 node arrival보다 넓어졌다는 점이다.

## docs-first reset과 canonical semantics 재고정

4월 9일에는 설계 축 자체를 다시 정리하는 docs-first reset이 나타났다. 구현을 그대로 옮기는 것이 아니라 문서와 생각, 철학을 먼저 가져가서 새 repo에서 다시 고정하는 편이 낫다는 판단이 explicit하게 나왔고, 이때 canonical 입력을 `주행 가능 의미 + 진행 의미`로 잠그려는 계획이 생겼다.

이 시점에 함께 고정된 것이 `선호는 입력이 아니라 field 구조가 생성한다`는 가설이다. 이전까지의 progression/gate/segment 논의가 path-reading intuition 쪽에 더 가까웠다면, 여기서는 그것을 어떤 종류의 semantic object로 설명할 것인지가 중심으로 올라왔다. SSC는 아이디어가 나온 source일 수는 있어도 canonical truth가 되어서는 안 된다는 경계도 이 시점에 더 분명해졌다.

## progress-tilted score space와 layer 분리

같은 시기에 score field 본체를 어떻게 상상했는지도 더 직접적으로 설명되기 시작했다. path를 만들어 내는 시스템보다, 주행 가능 공간 위에 점수 구조를 만들어 두면 downstream이 그 위에서 더 좋은 경로를 알아서 만들 수 있지 않겠느냐는 문제의식이 explicit하게 올라왔다. 사용자의 언어로는 이것이 `중력장처럼 돼있는 공간`, `진행방향으로 기울어진 점수 공간`이었다.

이 구간에서 남은 핵심은 두 가지다. 하나는 점수 구조의 주역이 바로 앞의 local optimum만 따라가게 하는 것이 아니라, 더 멀리 있는 더 좋은 진전이 ordering에 반영될 수 있어야 한다는 점이다. 다른 하나는 base score space와 safety/rule/dynamic 같은 예외 층을 같은 종류의 layer로 섞으면 안 된다는 것이다. 즉 이 시점부터 DPF는 단순 path score보다, progress-tilted score space와 exception layer 분리로 읽히기 시작했다.

## whole-space fabric instead of tube support

점수 구조가 무엇인지에 대한 raw objection도 같은 시기에 더 강해졌다. 사용자는 guide 주변에만 점수가 남는 tube support처럼 보이는 current morphology에 불만을 표시했고, `애초에 공간`, `염소뿔 사이를 메운 느낌`, `복소공간 스프링`, `꽈배기` 같은 표현으로 빈 공간이 없는 whole-space fabric을 상상했다.

이 전환은 단순히 더 부드러운 그림을 원했다는 뜻이 아니다. branch와 merge에서도 빈 공간이 생기지 않는 연속 surface, 진행방향 tilt가 공간 전체에 걸리는 ordering, 그리고 overlap이 생기더라도 그 판단은 다른 계층이 맡는다는 책임 분리가 함께 있었다. 이후 설계 문서에서 `tube support`가 비판의 대상이 되고, `whole-space field`가 더 적합한 표현으로 남게 된 배경이 여기 있다.

## Semantic Snapshot / Query Context / score function 언어

4월 10일에는 canonical contract 언어가 더 구체화됐다. 여기서 나온 핵심은 local map 자체의 의미와, 그 의미를 지금 어떤 기준과 시점에서 평가하는지를 분리해야 한다는 점이었다. 그 결과 `Semantic Input Snapshot`과 `Query Context`라는 언어가 올라왔고, `ego_pose`, `local_window`, branch winner, support/confidence 같은 항목이 canonical truth가 아니라 experiment 또는 context 쪽이라는 boundary가 함께 생겼다.

또 하나의 중요한 질문은 이 작업을 어떤 말로 불러야 하는가였다. `선호장`, `score function`, `goal cost function` 같은 표현이 후보로 올라왔고, 사용자 쪽에서는 분야 언어를 참고하되 원래 의도와 어긋나는 용어로 자기 생각을 밀어 넣고 싶어 하지는 않았다. 이 구간이 남긴 것은, DPF가 input semantics와 query-time context를 분리해 읽혀야 한다는 점과, naming itself도 설계의 일부라는 사실이다.

## DPF를 progress-preference device로 읽게 된 전환

이전까지의 progression/gate/segment/history가 path interpretation의 문제였다면, 4월 17일 이후에는 DPF 자체를 어떤 object로 볼 것인지가 다시 좁혀졌다. 여기서 사용자 쪽에서 가장 분명하게 제안한 framing은, DPF는 입력 경로를 참고해 `어디로 가는 것이 더 좋은지`를 기울여 주는 장치라는 것이었다.

이 framing은 path를 끝까지 붙잡는 장치와 구분된다. 입력 경로는 여전히 중요하지만, 그대로 복제해야 하는 경로라기보다 지금 어느 쪽이 더 나은 진전인지 읽는 기준으로 남는다. 이렇게 되면서 earlier gate/consume intuition은 path execution contract가 아니라 progress-preference를 읽는 더 이른 기원으로 다시 자리 잡게 됐다.

## longitudinal와 transverse에 대한 역할 재정의

progress-preference framing이 분명해지면서 longitudinal와 transverse를 보는 방식도 달라졌다. 이전보다 longitudinal가 더 주역이고, transverse는 구조를 완전히 잃지 않게 받쳐 주는 보조 성분이라는 생각이 강해졌다. path following이 중요하면 transverse를 더 강하게 둘 수 있지만, 더 효율적인 진전이나 더 좋은 라인을 고르는 것이 중요하면 longitudinal를 더 강하게 둘 수 있다는 식의 질문이 explicit하게 나왔다.

이 전환은 단순 gain tuning 이야기가 아니었다. base field가 corridor fidelity를 얼마나 책임져야 하는가, 그리고 progression ordering을 더 멀리 있는 더 나은 상태까지 얼마나 미리 기울여야 하는가를 다시 묻게 만들었다. `Normalized` visualization은 계산을 막지 않고 화면 대비만 다시 펴는 것이라는 구분도 이때 분리됐다.

## planner / behavior와의 책임 경계가 분리된 과정

DPF가 진행 선호를 주는 장치라는 framing이 굳어지면서, detailed path responsibility는 planner와 behavior가 더 많이 가져가야 한다는 생각도 같이 분명해졌다. 사용자의 표현으로는, 필요한 조정은 파라미터로 만들 수 있어도 실제 path 책임까지 DPF가 다 져야 하는 것은 아니라는 쪽이었다.

이 경계는 reverse를 보는 방식에도 이어졌다. reverse를 완전히 별도 특수 모드로 분리하기보다, 진행방향 성분의 기울기를 반대로 두는 경우로 읽는 편이 더 맞다는 생각이 나왔다. progression 방향 정의를 어떻게 두느냐가 중요하다는 점이 여기서 다시 강조됐다.

## 비교 방법론이 설계와 분리된 과정

최근에는 DPF를 어떻게 설명할지뿐 아니라, 그것을 baseline과 어떻게 공정하게 비교할지도 별도의 설계 문제로 떠올랐다. 여기서 사용자가 가장 분명하게 제기한 우려는, DPF가 더 무겁다고 해서 단순히 control frequency를 낮춘 뒤 baseline과 결과만 비교하면 제대로 된 실험이 아니라는 점이었다.

이 문제의식은 비교를 하나로 보지 않고 세 층으로 분리하게 만들었다. 첫째는 같은 real-time target 안에서 baseline과 DPF를 비교하는 benchmark다. 둘째는 같은 MPPI budget을 유지한 채 achieved Hz와 overrun을 비교하는 구조 비용 benchmark다. 셋째는 MPPI budget과 behavior 파라미터를 sweep해 성능 대 비용 frontier를 보는 tuning study다.

이 전환으로 인해 설계 history는 object 자체뿐 아니라, 그 object를 공정하게 읽는 방법론도 분리해서 기록해야 한다는 단계까지 왔다. 다만 이것은 latest design object 그 자체라기보다, 그 object를 평가하고 설명하는 후속 구조로 남는다.

## branch/split 실험이 baseline discipline 문제를 드러낸 과정

분기와 U-turn morphology를 비교하기 시작한 뒤에는, historical snapshot과 transverse 실험이 빠르게 쌓이면서 baseline 자체가 무엇인지 흐려지는 문제가 드러났다. 사용자는 workspace가 branch/split investigation 이후 더러워졌고, 그 이유 중 하나가 승인 없이 실험 상태를 baseline으로 올린 것이라고 직접 지적했다.

이 지점이 남긴 교훈은 설계 object와 별도로 workflow discipline을 잠가야 한다는 점이다. branch/split morphology investigation은 separate worktree에서 계속할 수 있지만, `main` 승격이나 baseline 재정의는 explicit user approval 뒤에만 이뤄져야 한다. 이건 DPF 수식 자체를 바꾸는 전환은 아니지만, 이후 설계 실험을 어떤 절차로 다뤄야 하는지에 대한 중요한 correction으로 남는다.

## B11 cleanup과 adapter 입력 경계 확장

`B11 = 465398d`로 transverse object를 raw visible progression guide polyline distance로 단순화한 뒤에는, 그 behavior baseline 위에 남은 stale public semantics와 raw adapter 경계를 한 번 더 정리해야 하는 문제가 남았다. 사용자는 old `progression_n_hat` / `progression_transverse_component` naming이 더 이상 실제 의미와 맞지 않고, raw adapter도 explicit progression guide만 고집해서는 안 된다고 봤다.

이 follow-up에서 남은 핵심은 두 가지였다. 첫째, dominant guide score에 실제로 들어가는 transverse term과 exported public detail channel을 정확히 일치시키는 것이다. 둘째, raw adapter boundary에서 progression source를 explicit progression, global plan, bounded drivable-only reconstruction으로 넓히되, ambiguous branch topology는 fail-fast로 유지하는 것이다. 이건 새 behavior baseline 승격이 아니라 `B11` 위 cleanup/contract expansion으로 남는다.

## 현재 시점의 설계 위치

현재까지의 흐름을 묶으면, DPF는 segment consume과 gate 통과 직관에서 출발해, blocked case에서는 frontier/local splice가 별도로 움직여야 한다는 pressure를 겪고, docs-first reset을 통해 `주행 가능 의미 + 진행 의미`와 `선호는 field 구조가 만든다`는 semantics로 다시 고정됐다. 그 위에 progress-tilted score space, whole-space fabric, Semantic Snapshot/Query Context 분리, progress-preference framing, longitudinal 주역화, planner/behavior 책임 분리가 겹쳐져 있다.

동시에, 이 전체 서사는 raw note anchor가 먼저 있어야 한다는 요구도 분명히 만들었다. 그래서 지금의 history와 latest design 문서는 넓은 source reread를 거쳐 raw note를 먼저 고정한 뒤 따라가는 파생 문서로 다시 정렬되고 있다. 최근에는 baseline 승격 승인 discipline과 `B11` 위 cleanup/contract expansion까지 같은 workflow correction으로 잠겨 있다.
