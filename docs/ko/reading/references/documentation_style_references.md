# 문서 스타일 참고 자료

> 참고용 기록 문서다. 현재 문서 작성 판단은 `docs/ko/explanation/documentation_writing_principles.md`를 기준으로 읽는다.

이 문서는 `local-reference-path-cost`의 문서 품질을 다듬을 때 참고한 공식 자료를 기록한다.
canonical 문서에 외부 기준을 그대로 인용하지 않기 위해,
출처와 핵심 원칙, 그리고 이 repo에 적용할 때의 해석 포인트만 분리해 둔다.

## 1. Diátaxis

- 출처: `https://diataxis.fr/`
- 참고한 핵심 원칙:
  - documentation은 user need에 따라 tutorial, how-to guide, reference, explanation으로 나뉜다
  - content, style, architecture를 함께 보되 네 역할을 섞지 않는다
- 우리 repo 적용 포인트:
  - 현재 `explanation / reference / how-to / status / reading / internal` 구조를 유지한다
  - explanation과 reference가 같은 말을 다른 밀도로 반복하지 않게 한다
  - `docs/ko/index.md`가 문서 포털을 맡고, 개별 문서는 자기 역할의 질문에만 답하게 한다

## 2. Google Technical Writing

- 출처:
  - `https://developers.google.com/tech-writing/one/paragraphs`
  - `https://developers.google.com/tech-writing/one/documents`
  - `https://developers.google.com/tech-writing/one/lists-and-tables`
- 참고한 핵심 원칙:
  - opening sentence가 문단의 중심점을 바로 잡아야 한다
  - 한 문단은 한 주제에 집중해야 한다
  - 문서는 scope와 non-scope를 분명히 해야 한다
  - 긴 prose를 무조건 유지하지 말고, 필요할 때는 목록과 표로 바꾼다
- 우리 repo 적용 포인트:
  - explanation 문서는 첫 문단에서 질문과 범위를 바로 말한다
  - reference는 가능한 한 표와 목록으로 찾아보기 중심 구조를 유지한다
  - roadmap/status는 scope와 non-scope를 짧게 명시한다

## 3. Microsoft 글쓰기 스타일 가이드

- 출처:
  - `https://learn.microsoft.com/en-us/style-guide/welcome/`
  - `https://learn.microsoft.com/en-us/style-guide/procedures-instructions/`
  - `https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions`
  - `https://learn.microsoft.com/en-us/style-guide/checklists/procedures-and-instructions-checklist`
- 참고한 핵심 원칙:
  - simple, straightforward style
  - crisp and clear wording
  - terminology consistency
  - procedure는 작업 중심이어야 하고, heading은 사용자가 무엇을 할 수 있는지 바로 보여 줘야 한다
  - step은 짧고 완결된 문장으로 쓰고, UI 안에서 어디서 행동하는지 먼저 알려 주는 편이 좋다
- 우리 repo 적용 포인트:
  - 핵심 용어는 첫 등장만 한국어+영문 병기하고, 그 뒤에는 더 짧은 표기로 통일한다
  - user-facing 문장과 internal working term이 조용히 다른 의미로 흐르지 않게 glossary와 docs를 맞춘다
  - 문서가 메타 설명으로 길어지지 않게 직접 정의하는 문장을 우선한다
  - in-app `Guide`는 “지금 무엇을 해야 하는가”를 먼저 답하고, `Parameter Help`는 knob reference를 담당하도록 역할을 분리한다

## 4. Kubernetes 문서 스타일 가이드

- 출처:
  - `https://kubernetes.io/docs/contribute/style/style-guide/`
  - `https://kubernetes.io/docs/ko/contribute/style/style-guide/`
- 참고한 핵심 원칙:
  - heading과 internal structure가 reader navigation을 돕는다
  - style guide는 rules보다 judgment를 중시한다
  - 용어와 capitalization, 구조를 일관되게 유지한다
- 우리 repo 적용 포인트:
  - 문서 제목 체계와 섹션 깊이를 과도하게 늘리지 않는다
  - `docs/ko/index.md`에서 처음 읽는 순서를 고정하고, 개별 문서 H1은 번호 없이 유지한다
  - 문서/코드/테스트가 공유하는 공개 용어는 표기와 의미를 같이 맞춘다

## 5. Red Hat 모듈형 문서

- 출처: `https://redhat-documentation.github.io/modular-docs/ko/`
- 참고한 핵심 원칙:
  - concept, procedure, reference module은 목적이 다르다
  - concept과 reference는 짧은 introduction이 필요하다
  - reference는 scan-friendly structure가 중요하다
  - procedure는 step-by-step task를 우선한다
- 우리 repo 적용 포인트:
  - explanation 문서는 concept에 가깝게 쓰되, 개념과 경계를 분리한다
  - reference 문서는 짧은 intro 뒤에 정의, 필수, optional, 비범위 순서를 유지한다
  - `parameter_lab.md`는 prerequisite, steps, expected outputs, limits 순서의 작업 중심 문서로 유지한다

## 현재 기준

이 문서는 공식 출처와 해석 포인트만 기록한다.
실제 판단 규칙은 `docs/ko/explanation/documentation_writing_principles.md`에 두고,
새로운 예외가 생기면 이 출처들을 다시 확인해 문서 품질 판단에 반영한다.
