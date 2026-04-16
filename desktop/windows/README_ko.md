Windows 실행기 안내

목적

- 바탕화면에는 바로가기 하나만 두고
- 실제 실행 파일은 모두 repo 안 `desktop/windows/` 아래에서 관리하기 위한 구조임

구성 파일

- `launch_parameter_lab.ps1`
  실제 Windows 실행 로직이 들어 있는 PowerShell 스크립트
- `launch_parameter_lab.cmd`
  바탕화면 바로가기가 직접 가리키는 진입점
- `Driving Preference Field Lab.ico`
  Windows 바로가기에서 사용하는 아이콘 파일
- `Driving Preference Field Lab.lnk`
  현재 머신에서 바로 복사해 사용할 수 있도록 repo 안에 함께 두는 바로가기 파일
- `install_desktop_shortcut.ps1`
  repo 안 바로가기와 바탕화면 바로가기를 함께 다시 생성하거나 갱신하는 설치 스크립트

권장 구조

- repo 안 실행 파일
  - `desktop/windows/launch_parameter_lab.ps1`
  - `desktop/windows/launch_parameter_lab.cmd`
  - `desktop/windows/Driving Preference Field Lab.ico`
  - `desktop/windows/Driving Preference Field Lab.lnk`
  - `desktop/windows/install_desktop_shortcut.ps1`
- 바탕화면
  - `Driving Preference Field Lab.lnk`

즉 바탕화면에는 `.lnk`만 남기고 실행 로직은 repo 안에서만 관리하는 구조임
- repo 안의 `.lnk`는 복사용 기준 파일 역할도 함께 함

실행 방식

- 바탕화면 바로가기는 `desktop/windows/launch_parameter_lab.cmd`를 직접 실행함
- `launch_parameter_lab.cmd`는 같은 폴더의 `launch_parameter_lab.ps1`를 호출함
- `launch_parameter_lab.ps1`는 Python 환경 확인, case 확인, probe 실행, Parameter Lab 실행을 담당함

장점

- 바탕화면에 별도 `ps1` wrapper를 둘 필요가 없음
- launcher 수정이 생겨도 repo 안 파일만 바꾸면 됨
- 실행기 관련 의도와 재현 방식이 repo 안에 남음

기본 실행 명령

- repo에서 직접 실행
  - `powershell -ExecutionPolicy Bypass -File .\desktop\windows\launch_parameter_lab.ps1`
- 또는
  - `.\desktop\windows\launch_parameter_lab.cmd`

바탕화면 바로가기 다시 만들기

- 아래 명령을 실행하면
  - `desktop/windows/Driving Preference Field Lab.lnk`
  - 바탕화면의 `Driving Preference Field Lab.lnk`
  두 파일이 모두 repo 안 실행기를 직접 가리키도록 갱신됨

`powershell -ExecutionPolicy Bypass -File .\desktop\windows\install_desktop_shortcut.ps1`

주의

- `.lnk`는 Windows 바로가기 파일이라 현재 머신의 경로를 기준으로 만들어짐
- 즉 repo 안에 두더라도 완전히 범용 템플릿은 아니고 현재 Windows 환경에 맞춘 reproduction asset임

환경 변수

- `DPF_PYTHON_EXE`
  - 기본 Python 실행 파일 경로를 덮어쓸 때 사용
- `DPF_CASE_PATH`
  - 기본 case 파일 대신 다른 case를 실행할 때 사용

현재 기본값

- Python
  - `%USERPROFILE%\anaconda3\envs\driving-preference-field\python.exe`
- Case
  - `cases/toy/straight_corridor.yaml`
- Profile preview
  - Windows에서는 `DPF_ENABLE_PROFILE_PLOTS=0`로 기본 비활성화

문제 발생 시 확인

- 바탕화면 로그 파일
  - `Driving Preference Field Lab.log`
- 먼저 확인할 항목
  - Python 경로가 실제 존재하는지
  - case 파일 경로가 실제 존재하는지
  - `PROBE_OK`가 로그에 찍혔는지

정리

- 앞으로 Windows 실행기 수정은 `desktop/windows/` 안에서만 하면 됨
- 바탕화면에는 바로가기만 있으면 됨
