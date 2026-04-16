# 문서 감사 인덱스

이번 감사는 `git ls-files` 기준 tracked 파일 전부를 대상으로 했다.
목표는 문서 본문을 다시 쓰기 전에, 어떤 파일군이 어떤 역할을 하고 있고 어디서 drift나 가독성 문제가 생기는지 먼저 고정하는 것이다.

감사 문서는 파일군별로 나눈다.

- [docs audit](./docs_audit.md)
- [src audit](./src_audit.md)
- [tests audit](./tests_audit.md)
- [root and supporting files audit](./root_audit.md)

다음 재작성 순서는 이 감사 문서들이 공통으로 가리키는 우선순위를 따른다.

1. `docs/ko/explanation/*`
2. `docs/ko/reference/*`
3. `docs/ko/how-to/*`
4. `docs/ko/status/*`
5. `docs/ko/reading/*`
6. `docs/ko/internal/*`
7. public-facing `src` 주석 / CLI help / docstring
