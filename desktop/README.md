Desktop launchers

This directory keeps repo-managed launcher files for each platform so that
reproduction logic lives in the repository instead of only in local desktop
shortcuts.

Structure

- `desktop/windows/launch_parameter_lab.ps1`
  Repo-managed Windows launcher for Parameter Lab
- `desktop/windows/launch_parameter_lab.cmd`
  Windows shortcut entrypoint that calls the PowerShell launcher
- `desktop/windows/install_desktop_shortcut.ps1`
  Helper script that creates a desktop shortcut on Windows
- `desktop/windows/README_ko.md`
  Korean guide for the Windows launcher layout
- `desktop/linux/launch_parameter_lab.sh`
  Repo-managed Linux launcher for Parameter Lab
- `desktop/linux/driving-preference-field-parameter-lab.desktop`
  Linux desktop entry for this machine and repo layout

Notes

- These launchers are reproduction-layer assets only
- They must not change field semantics, config semantics, or preset semantics
- Windows currently sets `DPF_ENABLE_PROFILE_PLOTS=0` by default because the
  profile preview path is still unstable there
- The default case is `cases/toy/straight_corridor.yaml`
- Override the Python executable on Windows with `DPF_PYTHON_EXE` if needed

Windows

Run the repo-managed launcher directly

`powershell -ExecutionPolicy Bypass -File .\desktop\windows\launch_parameter_lab.ps1`

Or create a desktop wrapper

`powershell -ExecutionPolicy Bypass -File .\desktop\windows\install_desktop_shortcut.ps1`

Linux

Run the repo-managed launcher directly

`./desktop/linux/launch_parameter_lab.sh`

The desktop entry in `desktop/linux/` is intended for the current Linux path
layout and can be copied into `~/.local/share/applications/` if desired.
