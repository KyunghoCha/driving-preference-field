# docs-first 재시작과 canonical semantics 재고정

## Date

- 2026-04-09

## Topic

- `docs-first reset`
- `canonical semantics`

## Source sessions

- confirmed materialized source: `$HOME/.codex/sessions/2026/04/09/rollout-2026-04-09T22-25-35-019d726b-6c39-7b80-8512-6d4e9d3e97b4.jsonl`
- this note captures the repo reset where the user narrows the project around documents, philosophy, and canonical semantics before implementation

## User original messages

> 문서에 우리가 하는거의 범위를 정확하게 명시를 해줘 논문에서도 그게 필요할거 같아서

> 디렉토리나 ws를 새로 파는게 나을까 지금 프젝 이름도 바꿔야 될거 같고 바꿀게 많은거 같은데 코어 문서들과 ~/Projects/PROMPTS를 들고 가서 새로 하는게 나을까 뭐가 낫다고 봐?

> 내 의도나 그런거 전부 문서에 명시 돼있지? 가져갈 문서들 가져가고 이사 하자

> 당연히 그대로 이사는 안하고 나는 문서랑 생각 철학 이런거만 가져가서 새로 만드는게 낫다고 생각하거든 아니면 문서도 거기 새로 만들던가 우선 거기 문서를 만들고 PROMPTS에 있는거 정독해서 형식대로 그리고 다시 구현하는게 낫지 않을까 싶어서

> PLEASE IMPLEMENT THIS PLAN:
> # `driving-preference-field` Docs-First 재시작 계획
>
> ## Summary
> - 새 workspace는 `/home/ckh/Projects/driving-preference-field` 로 고정한다.
> - 새 프로젝트는 **코드 이관 없이 문서부터 다시 세운다**.
> - 새 canonical의 중심은 다음으로 고정한다.
> - 외부에서 주어지는 주행 가능 의미를 입력으로 받는다
> - base driving preference field를 정의한다
> - obstacle/rule/dynamic은 별도 layer로 다룬다
> - runtime은 local 함수 평가가 가능하다

> PLEASE IMPLEMENT THIS PLAN:
> # `driving-preference-field` 전체 문서 정리 계획
>
> ## Summary
> - 새 canonical은 `주행 가능 의미 + 진행 의미`를 입력으로 받고, **선호는 입력이 아니라 field 구조가 생성한다**는 가설로 고정한다.
> - SSC 같은 실제 입력원은 canonical 본문에 넣지 않고 `docs/reading/`에서만 concrete example로 다룬다.

## Open questions at the time

- docs-first reset이 canonical semantics를 충분히 잠그는지
- `주행 가능 의미 + 진행 의미`를 이후 구현과 문서에서 얼마나 일관되게 유지할지
- SSC와 canonical 정의 사이의 거리를 어느 수준으로 둘지
