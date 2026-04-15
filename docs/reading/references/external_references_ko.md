# 외부 참고 문헌 기록

- 역할: reading
- 현재성: non-canonical
- 대상 독자: contributor, maintainer
- 다음으로 읽을 문서: [03. Base Field 기초](../../explanation/base_field_foundation_ko.md)

> 이 문서는 canonical truth가 아니다.
> 현재 상태: reading / references
> canonical 관련 문서: `docs/explanation/`, `docs/reference/`, `docs/how-to/`

작성일: 2026-04-09

이 문서는 `driving-preference-field`를 설계하고 구현할 때 실제로 참고한 외부 논문/글을 기록한다.

canonical truth는 여전히 `docs/explanation/`, `docs/reference/`, `docs/how-to/` 아래 문서에서 직접 정의한다. 이 문서는 canonical을 대신하지 않고, **무엇을 어디에 참고했는지**를 나중에 다시 추적할 수 있게 남겨두는 reference log다.

## 사용 원칙

- 이 목록은 현재까지 **실제로 참고한 외부 자료**만 적는다.
- “영감을 준 글”과 “현재 구현에 직접 반영된 자료”를 구분한다.
- exact current implementation이 아래 논문과 수학적으로 완전히 동일하다는 뜻은 아니다.
- canonical 정의와 current implementation note는 계속 `docs/explanation/`, `docs/reference/`, `docs/how-to/`에서 읽는다.

## 현재 구현에 직접 연결된 외부 참고 문헌

| 구분 | 자료 | 기록 이유 | 현재 연결 지점 |
| --- | --- | --- | --- |
| Smooth skeleton | Cem Yuksel, Scott Schaefer, John Keyser, *Parameterization and applications of Catmull-Rom curves*, Computer-Aided Design 43(7), 2011. DOI: `10.1016/j.cad.2010.08.008` | progression/branch guide polyline을 straight segment winner로 쓰지 않고, **centripetal Catmull-Rom**으로 더 부드럽게 resample하는 기준으로 참고했다. | `src/driving_preference_field/progression_surface.py`, `docs/reference/runtime_evaluation_contract_ko.md`, `docs/how-to/parameter_lab_ko.md` |
| Gaussian / normalized anchor blending | Donald Shepard, *A two-dimensional interpolation function for irregularly-spaced data*, Proceedings of the 1968 23rd ACM National Conference, 517-524, 1968. DOI: `10.1145/800186.810616` | current implementation에서 anchor를 winner로 고르지 않고 **정규화된 부드러운 weight blend**로 local space coordinates를 추정하는 방향을 정리할 때 참고했다. 현재 코드는 Shepard 식을 그대로 재현하지는 않지만, normalized weighted blending의 직접 배경으로 기록한다. | `src/driving_preference_field/progression_surface.py`, `docs/reference/runtime_evaluation_contract_ko.md`, `docs/how-to/parameter_lab_ko.md` |
| Skeleton-based seamless blending | Jules Bloomenthal, Ken Shoemake, *Convolution Surfaces*, SIGGRAPH 1991. PDF: `https://www.bloomenthal.com/JBloom/pdf/CSurfFinal.pdf` | guide/branch를 “winner reference”로 읽는 대신, **skeleton이 공간 형상을 만들고 surface가 매끈하게 이어진다**는 쪽의 핵심 영감으로 참고했다. branch gap을 비우지 않는 fabric-like field 방향을 정리할 때 직접 참고했다. | `docs/explanation/base_field_foundation_ko.md`, `docs/reference/runtime_evaluation_contract_ko.md`, `src/driving_preference_field/progression_surface.py` |

## 배경 / 개념 정리에 참고한 외부 글

| 구분 | 자료 | 기록 이유 | 현재 연결 지점 |
| --- | --- | --- | --- |
| Field-based implicit surface 역사 | James F. Blinn, *A Generalization of Algebraic Surface Drawing*, ACM Transactions on Graphics 1(3), 1982. DOI: `10.1145/357306.357310` | “경로 scorer”가 아니라 **공간 전체에 정의된 scalar field / implicit surface**라는 framing을 다시 잡을 때 배경 참고로 봤다. 현재 구현은 Blinn 식을 그대로 쓰지 않지만, score field를 space-first로 설명하는 데 도움이 됐다. | `docs/explanation/base_field_foundation_ko.md`, `docs/reference/base_field_terms_ko.md` |
| Compact-support / scattered-data 배경 | Holger Wendland, *Scattered Data Approximation*, Cambridge University Press, 2005. Cambridge Monographs on Applied and Computational Mathematics 17. | 예전 compact-support kernel 실험과 scattered anchor approximation을 더 넓게 읽기 위한 배경 자료로 참고했다. current implementation은 더 이상 Wendland kernel을 직접 쓰지 않지만, local field interpolation을 보는 배경 자료로는 남겨둔다. | background only |

## 현재 코드와 자료의 관계

- current implementation은 **closed-form convolution surface solver**가 아니다.
- current implementation은 **smooth skeleton + Gaussian normalized anchor blend** 방식이다.
- 따라서 위 참고 문헌은 아래처럼 읽는 것이 맞다.
  - Catmull-Rom: smooth skeleton 생성 기준
  - Shepard: normalized weighted anchor blending 기준
  - Wendland: compact-support 기반 초기 실험과 background 참고
  - Convolution Surfaces / Blinn: seam 없는 field-like surface를 바라보는 conceptual basis

즉 이 프로젝트의 current implementation은 위 문헌들을 그대로 재현한 것이 아니라, **research workspace의 local map score field 문제에 맞게 조합해 쓴 현재 구현체**다.

## 내부 문서와의 관계

- canonical SSOT: `docs/explanation/`, `docs/reference/`, `docs/how-to/`
- 진행 상태 / 계획: `docs/status/`
- archive / source-specific reading: `docs/reading/`

내부 SSOT 중 가장 먼저 볼 문서는 아래다.

- `docs/explanation/engineering_operating_principles_ko.md`
- `docs/explanation/base_field_foundation_ko.md`
- `docs/reference/runtime_evaluation_contract_ko.md`
- `docs/how-to/parameter_lab_ko.md`

## 참고 링크

- Catmull-Rom journal abstract: `https://doi.org/10.1016/j.cad.2010.08.008`
- Wendland paper DOI: `https://doi.org/10.1007/BF02123482`
- Convolution Surfaces PDF: `https://www.bloomenthal.com/JBloom/pdf/CSurfFinal.pdf`
- Blinn paper metadata: `https://authors.library.caltech.edu/records/8gefj-s7p14`
- Wendland book metadata: `https://www.cambridge.org/core/books/scattered-data-approximation/980EEC9DBC4CAA711D089187818135E3`
