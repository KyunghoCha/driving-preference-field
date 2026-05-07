# 운영 원칙

이 문서는 repo가 drift 없이 움직이기 위한 기본 방향을 적는다. 법전처럼 영원히 고정된 규칙을 나열하려는 문서가 아니다. 더 좋은 근거와 더 나은 운영 방식이 생기면 이 문서 자체도 바뀔 수 있다. 중요한 것은 복종이 아니라, `local-reference-path-cost`의 code health와 계약 일관성을 계속 더 좋게 만드는 것이다.

## 1. 증상보다 원인에서 시작한다

눈앞의 현상만 가리는 patch는 기본 선택이 아니다. 증상이 보이면 먼저 어떤 개념 드리프트, 어떤 layer 경계, 어떤 runtime 가정에서 왔는지 본다. 단기 workaround가 필요해도 본질 원인과 분리해 기록하는 편이 맞다.

문서도 같다. 독자가 헷갈린다면 보통 필요한 것은 note를 더 얹는 일이 아니라 canonical 문서를 더 분명하게 쓰고, stale wording을 제거하고, 계약을 명시적으로 만드는 일이다.

## 2. 문서와 현재 정의를 같이 움직인다

이 repo에서는 explanation, reference, how-to, status, UI help가 모두 working contract의 일부다. 코드가 current behavior를 바꾸면 그 behavior를 정의하거나 설명하는 문서도 같은 배치에서 같이 움직이는 편이 맞다. 문서가 canonical meaning을 바꾼다면 그 meaning을 구현한다고 주장하는 코드도 같이 확인되어야 한다.

중요한 것은 완벽한 동시성보다 silent drift를 막는 것이다. repo가 말하는 것과 실제 동작이 조용히 벌어지지 않게 하는 것이 기본 목표다.

## 3. 내부를 건드리기 전에 범위를 줄인다

요청은 먼저 실제 문제를 풀 수 있는 가장 작은 coherent slice로 줄이는 편이 좋다. scope가 흐려지면 구현 품질도 같이 흐려진다. 이 repo는 canonical meaning, runtime contract, current implementation, tooling, downstream integration을 한 번에 다 건드릴 때보다 한 layer씩 안정화할 때 더 잘 좋아진다.

그래서 future work를 current truth로 너무 일찍 올리지 않는다. research idea, adapter debate, downstream concern은 실제로 active contract에 들어오기 전까지 reading/history나 backlog에 두는 편이 맞다.

## 4. SSOT는 플랫폼과 downstream보다 위에 둔다

플랫폼 차이가 canonical meaning이 되면 안 된다. Linux, Windows 같은 환경은 launcher, packaging, troubleshooting에서 차이가 날 수 있지만 score semantics, config semantics, preset semantics는 그 위에 있어야 한다. 플랫폼 문제는 가능하면 dependency graph, capability detection, runtime fallback 같은 재현 계층에서 해결한다.

같은 논리는 SSC 같은 downstream consumer에도 적용된다. downstream이 설계를 검증할 수는 있어도, repo 자신의 계약을 조용히 대체하면 안 된다.

## 5. 실험은 clean baseline에서 분리한다

실험적 수정은 clean baseline에서 시작하고, 한 번에 한 가지 의미 있는 가설만 검증하는 편이 좋다. Git 사용 방식은 바뀔 수 있지만 운영 원칙은 같다. dirty state 위에 실험을 계속 덧칠해서, 어느 시도가 어떤 효과를 냈는지 설명할 수 없게 만드는 방향은 피한다.

이 원칙은 LRPC morphology 실험에서 특히 중요하다. 수식, support logic, coordinate definition, visualization이 서로 얽혀 있기 때문에, 분리와 추적 가능성을 편의보다 우선하는 쪽이 맞다.

## 6. 변경은 작게 묶고 검증은 끝까지 한다

작은 변경은 이해하기 쉽고, 리뷰하기 쉽고, 되돌리기도 쉽다. broad rewrite 자체가 가장 작은 coherent move가 아니라면, repo는 좁고 testable한 배치를 우선한다. 검증도 끝까지 가야 한다. docs, UI, runtime, export, experiment tooling을 건드렸다면 그 표면을 같이 확인해야 배치가 끝난다.

다만 예외는 있다. emergency fix, 신뢰할 수 있는 mechanical refactor, merge 대상이 아닌 exploratory spike는 예외가 될 수 있다. 이런 예외를 쓰는 경우에는 shortcut을 썼다는 사실과 이유를 남기는 편이 맞다.

## 7. correctness만 보지 말고 stale residue도 본다

리뷰는 "지금 돌아가나"에서 끝나지 않는다. 실험이 많은 repo는 stale formula path, unused knob, dead branch, outdated doc, 설명할 수 없는 복잡도를 쉽게 쌓는다. 출력이 얼핏 그럴듯해 보여도 이런 것들은 code-health 문제다.

그래서 기본 리뷰 질문은 더 넓다. 이 변경이 repo를 더 읽기 쉽게 만들었는지, 더 비교 가능하게 만들었는지, 더 진화시키기 쉽게 만들었는지를 같이 본다. 그렇지 않다면 방향 자체를 다시 생각하는 편이 맞다.

## 8. 이 문서도 운영과 함께 갱신한다

이 원칙들은 기본값이지 영구 불변 규칙이 아니다. 더 나은 baseline discipline, 더 나은 review 습관, 더 나은 실험 운영 방식이 보이면 이 문서도 명시적으로 같이 갱신한다. 안정적인 SSOT는 중요하지만, 얼어붙은 프로세스는 목표가 아니다.
