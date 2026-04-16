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
  Helper script that creates desktop and repo-local `.lnk` files on Windows
- `desktop/windows/README_ko.md`
  Korean guide for the Windows launcher layout
- `desktop/linux/launch_parameter_lab.sh`
  Repo-managed Linux launcher for Parameter Lab
- `desktop/linux/install_desktop_entry.sh`
  Helper script that renders an installed Linux desktop entry for the current
  repo location
- `desktop/linux/driving-preference-field-parameter-lab.desktop.in`
  Linux desktop entry template with placeholders
- `assets/parameter_lab_launcher.svg`
  Shared launcher icon source for Linux
- `assets/parameter_lab_launcher.ico`
  Shared launcher icon for Windows shortcuts

Notes

- These launchers are reproduction-layer assets only
- They must not change field semantics, config semantics, or preset semantics
- The default case is `cases/toy/straight_corridor.yaml`
- Override the Python executable on Windows with `DPF_PYTHON_EXE` if needed
- Profile preview is optional tooling. If plotting dependencies fail, Parameter
  Lab should still launch and degrade the preview pane instead of crashing.

Windows

Run the repo-managed launcher directly

`powershell -ExecutionPolicy Bypass -File .\desktop\windows\launch_parameter_lab.ps1`

Or create a desktop wrapper

`powershell -ExecutionPolicy Bypass -File .\desktop\windows\install_desktop_shortcut.ps1`

Linux

Run the repo-managed launcher directly

`./desktop/linux/launch_parameter_lab.sh`

Create an installed desktop entry for the current repo path

`./desktop/linux/install_desktop_entry.sh`

The Linux desktop entry is generated at install time so the repo does not carry
machine-specific absolute paths.
