# 루트 및 지원 파일 감사

이 감사는 root-level tracked 파일과 supporting asset 파일군을 함께 본 결과를 정리한다.

## 감사 범위

### Root-level tracked files 7개

- `README.md`
- `environment.yml`
- `.gitattributes`
- `.gitignore`
- `.github/workflows/ci.yml`
- `LICENSE`
- `run-parameter-lab.sh`

### Supporting files

- `scripts/launch_parameter_lab.sh`
- `desktop/linux/driving-preference-field-parameter-lab.desktop.in`
- `desktop/linux/install_desktop_entry.sh`
- `assets/parameter_lab_launcher.svg`
- `assets/parameter_lab_launcher.ico`
- `cases/toy/*.yaml` 8개
- `fixtures/adapter/*` 4개
- `presets/lab/*.yaml` 12개

## 현재 역할

- root:
  - repo landing page
  - environment/CI policy
  - launcher entrypoint
- cases/fixtures/presets:
  - toy case와 generic adapter fixture, repeatable preset pack
- scripts/desktop/assets:
  - Parameter Lab 실행 surface

## 실제 상태

- `README.md`는 짧은 landing page 역할을 하고 있다.
- environment와 launcher surface도 단순하고 목적이 분명하다.
- toy cases와 adapter fixtures는 Phase 4/5 acceptance와 generic source adapter를 지탱하는 최소 세트를 갖추고 있다.
- preset pack도 baseline/reference/downstream experiment를 구분하는 metadata를 포함한다.
- desktop launcher와 icon은 사용자 진입 surface를 제공한다.

## 문제 유형

### 1. CI 엄격도

- `.github/workflows/ci.yml`에서 Windows job은 여전히 `experimental: true`와 `continue-on-error`로 남아 있다.
- cross-platform drift를 강하게 막는 기준과는 아직 완전히 맞지 않는다.

### 2. root surface와 문서 포털의 책임 분리

- `README.md`는 현재 잘 줄어든 상태지만,
  문서 포털과 landing page의 역할 차이를 계속 유지해야 한다.
- 이후 문서 재작성 때 README가 다시 상세 설명을 끌어오지 않게 주의해야 한다.

### 3. fixture/preset pack의 설명 부재

- 데이터 파일 자체는 잘 정리돼 있지만,
  file pack 전체를 소개하는 짧은 안내 문서는 없다.
- 현재는 문서와 테스트를 통해 의미를 복원해야 한다.

### 4. launcher surface의 환경 의존성

- `scripts/launch_parameter_lab.sh`는 conda path와 local path를 전제로 한다.
- 의미 drift 문제는 아니지만,
  재현성 audit에서는 환경 의존 표면으로 계속 관리해야 한다.

## 유지할 것

- 짧은 `README.md`
- current launcher path
- toy / fixture / preset 세트의 현재 구조
- `.gitattributes` 기반 line-ending control
- root에서 docs 포털로 보내는 구조

## 수정이 필요한 것

- Windows CI를 언제 strict로 끌어올릴지 결정 필요
- cases/fixtures/presets pack을 소개하는 최소 안내 경로 검토
- launcher/environment surface의 재현성 note 점검

## 보류할 것

- launcher 재설계
- preset pack의 대규모 재구성
- case/fixture schema 변경
