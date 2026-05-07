# Archive Score Field 메모

> archive 문서에서 건져 올린 아이디어를 모아 둔 reading note다. 현재 정의는 canonical 문서를 기준으로 읽는다.

archive 문서에서 현재도 참고 가치가 있는 아이디어를 reading note 수준으로만 정리한다.

## 계속 참고할 아이디어

### 1. trajectory보다 앞선 표현 계층

주행 표현은 discrete path나 trajectory보다 앞단에서 정의될 수 있다. optimizer나 planner가 소비할 base structure를 먼저 세울 수 있다는 관점은 계속 유효하다.

### 2. layer 분리 필요성

ideal motion ordering를 담는 층과 obstacle / rule / dynamic exception을 담는 층은 구분되어야 한다는 문제의식은 계속 유지할 가치가 있다.

### 3. visualization과 canonical의 분리

full raster는 설명과 디버깅에는 유용하지만, canonical 표현 그 자체일 필요는 없다는 관점은 계속 참고할 만하다.

### 4. local evaluation 가능성

field가 의미론적으로는 넓은 공간 구조를 갖더라도, runtime 계산은 지역적 analytic evaluation로 구현할 수 있다는 방향은 계속 유지할 수 있다.

## 왜 reading으로만 남기는가

archive 문서는 형성 과정과 실험 흔적을 담고 있기 때문에, 현재 canonical 문서와 같은 층에서 읽으면 정의가 흔들릴 수 있다. 따라서 archive 문서는 아이디어 참고와 reading note로만 유지한다.
