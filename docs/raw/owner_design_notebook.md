# Owner Design Notebook

이 문서는 사용자 최신 설계 생각을 주제별 최신본으로 정리하는 non-canonical notebook이다. raw note가 원문 보존을 맡고, tracker가 시간 변화 추적을 맡는다면, 이 문서는 “지금 사용자 생각이 무엇인가”를 한 번에 읽히게 만드는 층이다.

current truth, 구현 계약, public claim은 계속 canonical docs에서만 고정한다. 이 문서는 canonical replacement가 아니라 owner-origin conceptual notebook이다.

## DPF가 책임지는 것

### 현재 사용자 framing

- DPF는 입력 경로를 참고해서 **어디로 가는 게 더 좋은지**를 기울여 주는 장치에 가깝다.
- detailed path를 강하게 고정하는 책임은 DPF보다 downstream planner / behavior가 더 많이 져야 한다.

### 핵심 문장

- “애초에 입력에 경로가 부분이긴 하지만 결국 어디로 가는게 좋냐는거잖아”
- “행동계획이나 걔들이 책임 지겠지 우리는 그걸 책임지면 안되는거야”

### 왜 이 생각이 나왔는가

- 최근 U-turn, `progression_tilted`, `longitudinal` vs `transverse` 대화에서 DPF가 corridor를 너무 강하게 붙잡는 장치인지, upstream preference를 주는 장치인지가 반복해서 문제로 떠올랐다.

### 관련 raw notes

- [진행방향 성분과 횡방향 성분 비중](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)
- [DPF를 진행 선호 장치로 보는 생각](./notes/2026-04-17-dpf-as-progress-preference-device.md)

### canonical docs와의 관계

- [Base Field 기초](../ko/explanation/base_field_foundation.md)와 닿아 있지만, 아직 canonical wording으로 확정된 상태는 아니다.

### 현재 열린 쟁점

- DPF와 downstream planner 사이의 responsibility boundary를 어디서 자를지
- local corridor fidelity를 base field가 어디까지 책임져야 하는지

## 진행방향 성분과 횡방향 성분

### 현재 사용자 framing

- `longitudinal`가 더 주역이 되고, `transverse`는 corridor를 완전히 잃지 않게 받쳐주는 정도일 수 있다.
- path following이 더 중요할 때는 `transverse`를 강하게, 더 효율적인 진전이 중요할 때는 `longitudinal`를 강하게 두는 방향이 자연스럽다.

### 핵심 문장

- “진행방향 성분이 메인으로 가고 횡방향성분은 그렇게 강하지 않아도 될거 같아”
- “경로 따라가는게 중요하면 횡방향성분을 강하게 하고 빨리 가는게 중요하면 진행방향 성분을 강하게 하고”

### 왜 이 생각이 나왔는가

- 실제 case에서 `longitudinal`가 우연히 더 강하게 보였을 때 경로 효율이 더 좋아 보였고, 현재 DPF가 center-following을 과하게 책임지는 것 아닌지 의문이 생겼다.

### 관련 raw notes

- [진행방향 성분과 횡방향 성분 비중](./notes/2026-04-17-longitudinal-vs-transverse-weighting.md)

### canonical docs와의 관계

- 아직 canonical formula 설명이나 parameter guide에 직접 반영되지 않았다.

### 현재 열린 쟁점

- 이것이 단순 parameter tuning인지, DPF object definition인지
- `Normalized` visualization이 절대 dominance를 얼마나 가리는지

## planner / behavior와의 책임 경계

### 현재 사용자 framing

- DPF는 optimizer/planner upstream에서 preference를 주고, 실제 detailed path responsibility는 planner / behavior가 더 많이 져야 한다.
- 후진 같은 경우도 진행방향 성분을 반대로 기울이는 식의 framing이 더 자연스럽다는 intuition이 있다.

### 핵심 문장

- “후진을 하면 진행방향 성분만 위로 기울게 하면 되는거라 그런식으로 생각을 했거든”
- “그럼 행동계획이나 걔들이 책임 지겠지 우리는 그걸 책임지면 안되는거야”

### 왜 이 생각이 나왔는가

- DPF가 path-following device와 progress-preference device 사이에서 어디에 가까운지에 대한 대화가 계속 이어졌고, 사용자 쪽에서는 후자에 더 무게를 두는 framing이 반복해서 나왔다.

### 관련 raw notes

- [DPF를 진행 선호 장치로 보는 생각](./notes/2026-04-17-dpf-as-progress-preference-device.md)

### canonical docs와의 관계

- [프로젝트 개요](../ko/explanation/project_overview.md), [Base Field 기초](../ko/explanation/base_field_foundation.md)의 일부 문장과 닿아 있지만, 책임 경계 wording은 아직 이 notebook 쪽이 더 직접적이다.

### 현재 열린 쟁점

- DPF가 planner보다 덜 책임지는 것으로 canonical wording을 좁혀야 하는지
- reverse / branch / merge behavior를 이 framing에서 어떻게 설명할지

## raw thought 기록 workflow

### 현재 사용자 framing

- raw에는 사용자 채팅 원문을 최대한 그대로 남기고, assistant는 필요할 때만 분리해서 넣는다.
- raw note와 별도로 최신 사용자 생각을 정리하는 design notebook이 필요하다.
- `.codex` 기록은 source material로 활용하되, 전체 로그를 그대로 문서화하지 않는다.

### 핵심 문장

- “내가 한 대화들을 넣으라는거지 내가 채팅에 친것들을”
- “raw에는 내 생각을 넣는게 좋을까 내 채팅을 넣는게 좋을까”
- “가장 최신에 내 생각들을 추적해서 정리를 하는 느낌이었어”

### 왜 이 생각이 나왔는가

- raw note 1차에서 원문 보존은 시작됐지만, 최신 사용자 철학/개념을 한 번에 읽을 문서가 없고 referential fragment도 남아 있어서 추가 구조가 필요해졌다.

### 관련 raw notes

- [raw thought 기록 workflow](./notes/2026-04-17-raw-thought-capture-workflow.md)

### canonical docs와의 관계

- [문서 작성 원칙](../ko/explanation/documentation_writing_principles.md)과 [실험 계획](../ko/status/experiment_plan.md)의 workflow boundary와 닿지만, canonical replacement는 아니다.

### 현재 열린 쟁점

- `.codex` historical backfill을 어디까지 할지
- referential fragment를 항상 앞뒤 원문으로 풀지, 일부는 assistant context를 허용할지
