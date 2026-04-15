# 운영 원칙

이 문서는 `driving-preference-field`를 설계하고 구현할 때 무엇을 먼저 지키는지 설명한다. 여기서 다루는 원칙은 개별 patch 취향이 아니라, repo 전체의 drift를 막고 SSOT를 유지하기 위한 판단 기준이다. README, canonical 문서, 구현, 테스트, 실험 기록은 모두 이 원칙 위에서 맞춰야 한다.

## 문제를 다루는 방식

눈앞의 현상만 가리는 patch는 넣지 않는다. 증상이 보이면 먼저 어떤 개념 드리프트에서 왔는지 본다. 단기 workaround가 필요하더라도 본질 원인과 분리해 기록해야 한다.

근본 원인을 볼 때는 모델 수준, layer 수준, runtime 수준을 나눠서 본다. 특정 수식 하나가 이상해 보여도 입력 semantics, composition, visualization을 함께 의심해야 한다. 한 부분만 만져 해결된 것처럼 보이면 전체 계약을 다시 확인한다.

또 특정 그림, 특정 수식, 특정 파일에 매몰되지 않는다. 항상 연구 범위 SSOT, 설계 SSOT, 구현 SSOT, internal working notes의 경계를 같이 본다. 부분 수정으로 전체 contract가 흐려지면 그 수정은 잘못된 것으로 본다.

모르는 것은 추측으로 메우지 않는다. local truth가 있으면 먼저 읽고, 그래도 불명확하면 검색해 근거를 확보한다. 끝까지 불명확하면 불확실성을 문서와 답변에 직접 남긴다.

## 문서와 현재 정의

이 repo에서는 문서가 구현보다 뒤따라가면 안 된다. 설계가 바뀌면 관련 canonical 문서가 같이 움직여야 하고, 문서와 코드가 다르면 코드보다 먼저 문서 drift를 의심한다. 구현을 먼저 밀어 넣고 나중에 설명을 맞추는 방식은 허용하지 않는다.

문서와 코드 변경은 현재 truth를 직접 정의하는 방식으로 쓴다. canonical 문서는 특정 과거 문서, 특정 예시, 특정 구현체, 특정 프레이밍에 기대어 중심 개념을 설명하지 않는다. 코드와 주석도 비교 서술보다 현재 계약, 현재 입력, 현재 의도를 직접 말해야 한다.

역사적 맥락, 대안 비교, 구현체별 참고 사항이 필요하면 reading 자료나 별도 메모로 분리한다. canonical은 현재 정의를 고정하는 곳이고, history나 proposal은 그 주변을 설명하는 곳이다. 둘을 섞으면 독자는 현재 truth와 검토 중인 생각을 구분하기 어려워진다.

왜 이런 field를 정의하는지, 왜 layer를 분리하는지, 왜 runtime contract를 그렇게 두는지는 문서와 주석에 직접 남긴다. 의도를 shell history나 채팅 맥락에만 남기지 않는다. 문서만 읽어도 현재 canonical과 current implementation을 복원할 수 있어야 한다.

## 범위와 비교 방법

한 번에 다 하려 하지 않는다. 현재 단계에서 무엇을 하지 않을지도 같이 적고, 구현 범위를 넘는 것은 next step으로 남긴다. 지금 질문이 base field 자체인지, optimizer 결합인지, UI나 도구 문제인지 먼저 구분해야 한다.

연구용 비교는 코드 분기보다 config와 preset을 우선한다. 같은 case와 같은 semantic snapshot 위에서 baseline과 candidate를 비교하고, 함수 family와 gain 실험도 코드 수정 반복보다 도구와 preset 기록을 통해 반복 가능하게 만든다.

시각화는 예뻐 보이는 화면보다 해석 가능한 스케일을 우선한다. 일반 채널 heatmap은 0을 절대 최소값으로 두는 채널별 고정 스케일을 기본으로 하고, diff heatmap은 0 중심 대칭 스케일을 기본으로 둔다. 상대 정규화는 탐색용 보조 모드로만 허용하고, 그때도 현재 표시 범위와 단위를 함께 드러낸다.

## SSOT와 크로스플랫폼

archive repo와 새 repo의 역할을 섞지 않는다. archive 실험 결과를 새 canonical truth로 승격하지 않고, 한국어 user-facing 문서와 영어 internal note가 조용히 다른 의미를 가지지 않게 한다. drift 방지는 기능 추가보다 먼저 지켜야 하는 기본 규칙이다.

다른 머신에서 한 작업도 같은 SSOT에 남긴다. Ubuntu, Windows, 다른 노트북, 다른 workstation에서 한 작업이라도 canonical 의미 변경은 같은 repo 문서 SSOT에 기록해야 한다. 다른 머신에서 구현한 현재 수식, runtime contract, preset 의미 변경도 merge 전에 관련 문서를 같이 갱신한다.

크로스플랫폼 차이는 의미가 아니라 재현 방식으로만 다룬다. 운영체제 차이로 field semantics, config semantics, preset semantics가 달라지면 안 된다. 플랫폼 차이는 환경 준비, line ending, 경로 처리, CI 구성 같은 재현 계층에서 해결하고, 특정 OS에서만 우연히 맞는 동작이나 렌더 결과를 canonical truth로 올리지 않는다.
