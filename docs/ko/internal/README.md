# 내부 문서 운영 원칙

이 디렉터리는 `driving-preference-field`의 내부 작업 메모를 담는다. 사용자에게 직접 보여 주는 SSOT는 아니고, 우선순위 정리, 작업 용어, 감사 메모 같은 내부 기록을 두는 곳이다.

## 목적

- 내부 작업 메모를 사용자 문서와 분리한다.
- 한국어 SSOT의 범위를 조용히 넓히지 않으면서 작업 흔적을 남긴다.
- 우선순위, 용어, 감사 결과를 한곳에서 복원할 수 있게 한다.
- 사용자 문서와 별도로 내부 판단 근거를 정리한다.

## 규칙

- 사용자 문서 SSOT는 계속 `docs/ko/explanation/`, `docs/ko/reference/`, `docs/ko/how-to/`, `docs/ko/status/`가 맡는다.
- `docs/ko/internal/`은 작업 메모, 우선순위, glossary, 감사 메모만 둔다.
- internal note는 `docs/ko/explanation/research_scope.md`를 넘어서는 주장이나 범위를 조용히 추가하면 안 된다.
- internal note 때문에 architecture나 scope가 바뀌면, 대응하는 한국어 SSOT를 먼저 갱신해야 한다.
