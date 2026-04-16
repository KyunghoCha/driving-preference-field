# 운영 원칙

이 문서는 `driving-preference-field`를 설계하고 구현할 때 무엇을 먼저 지켜야 하는지 설명한다. 여기서 다루는 것은 코드 스타일 취향이 아니라, repo 전체의 drift를 막고 SSOT를 유지하기 위한 판단 기준이다. README, canonical 문서, 구현, 테스트, 실험 기록은 모두 이 원칙 위에서 맞아야 한다.

## 1. 증상보다 원인을 먼저 본다

눈앞의 현상만 가리는 patch는 넣지 않는다. 증상이 보이면 먼저 어떤 개념 드리프트, 어떤 layer 경계, 어떤 runtime 가정에서 왔는지 본다. 단기 workaround가 필요해도 본질 원인과 분리해 기록해야 한다.

특정 그림이나 특정 파일에 매몰되지 않는 것도 같은 이유다. 수식 하나가 이상해 보여도 입력 semantics, composition, visualization, preset, tooling을 같이 의심해야 한다. 한 부분만 만져 해결된 것처럼 보이면 전체 계약을 다시 확인한다.

모르는 것은 추측으로 메우지 않는다. local truth가 있으면 먼저 읽고, 그래도 불명확하면 검색해 근거를 확보한다. 끝까지 불명확하면 불확실성을 문서와 답변에 직접 남긴다.

## 2. 문서와 현재 정의를 같이 움직인다

이 repo에서는 문서가 구현보다 뒤따라가면 안 된다. 설계가 바뀌면 관련 canonical 문서가 같은 배치에서 같이 움직여야 한다. 구현을 먼저 밀어 넣고 나중에 설명을 맞추는 방식은 허용하지 않는다.

canonical 문서는 현재 truth를 직접 정의해야 한다. 특정 예시나 특정 과거 문서, 특정 구현체를 빌려 핵심 개념을 설명하지 않는다. 역사적 맥락, 대안 비교, proposal history는 reading 자료로 분리하고, canonical은 지금 정의와 지금 계약만 말해야 한다.

의도도 채팅 로그에만 남기지 않는다. 왜 이런 field를 정의하는지, 왜 layer를 분리하는지, 왜 runtime contract를 그렇게 두는지는 문서와 주석에 직접 남긴다. 문서만 읽어도 current canonical과 current implementation을 복원할 수 있어야 한다.

## 3. 범위를 먼저 자른다

한 번에 다 하려 하지 않는다. 현재 단계에서 무엇을 하지 않을지도 같이 적고, 구현 범위를 넘는 것은 next step으로 남긴다. 지금 질문이 base field 자체인지, optimizer 결합인지, UI/툴 문제인지 먼저 구분해야 한다.

연구용 비교는 코드 분기보다 config와 preset을 우선한다. 같은 case와 같은 semantic snapshot 위에서 baseline과 candidate를 비교하고, 함수 family와 gain 실험도 코드 수정 반복보다 도구와 preset 기록을 통해 반복 가능하게 만든다.

시각화도 같은 기준으로 본다. 예뻐 보이는 화면보다 해석 가능한 스케일을 우선하고, 무엇이 base field이고 무엇이 costmap/overlay인지 같은 뜻이 섞이지 않게 한다.

## 4. SSOT를 플랫폼보다 위에 둔다

archive repo와 현재 repo의 역할을 섞지 않는다. archive 실험 결과를 새 canonical truth로 승격하지 않고, 한국어 user-facing 문서와 영어 internal note가 조용히 다른 의미를 가지지 않게 한다. drift 방지는 기능 추가보다 먼저 지켜야 하는 기본 규칙이다.

다른 머신에서 한 작업도 같은 SSOT에 남긴다. Ubuntu, Windows, 다른 workstation에서 한 작업이라도 canonical 의미 변경은 같은 repo 문서 SSOT에 기록해야 한다. merge 전에 관련 문서를 같이 갱신한다.

크로스플랫폼 차이는 의미가 아니라 재현 방식으로만 다룬다. 운영체제 차이로 field semantics, config semantics, preset semantics가 달라지면 안 된다. 플랫폼 차이는 환경 준비, 경로 처리, launcher, CI 같은 재현 계층에서 해결하고, 특정 OS에서 우연히 맞는 동작을 canonical truth로 올리지 않는다.

## 5. 변경은 작게, 검증은 끝까지

도구나 문서를 고칠 때도 같은 원칙을 쓴다. 먼저 현재 구조를 읽고, 바꿔야 할 층만 건드리고, regression으로 다시 잠근다. 필요 없는 중복 UI, 중복 문서, 중복 설정은 늘리지 않는다.

즉 이 repo의 기본 원칙은 단순하다. 원인을 먼저 보고, 문서와 구현을 같이 움직이고, 범위를 먼저 자르고, 플랫폼 차이를 의미 차이로 올리지 않고, 변경 뒤에는 반드시 다시 검증한다.
