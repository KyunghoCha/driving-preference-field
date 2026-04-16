$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Driving Preference Field Lab.lnk"
$repoLauncherPath = Join-Path $repoRoot "desktop\windows\launch_parameter_lab.cmd"
$repoShortcutPath = Join-Path $PSScriptRoot "Driving Preference Field Lab.lnk"
$repoIconPath = Join-Path $repoRoot "assets\parameter_lab_launcher.ico"

if (-not (Test-Path -LiteralPath $repoLauncherPath)) {
    throw "Repo launcher not found: $repoLauncherPath"
}

function Set-Shortcut {
    param([string]$ShortcutPath)

    $wshShell = New-Object -ComObject WScript.Shell
    $shortcut = $wshShell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $repoLauncherPath
    $shortcut.Arguments = ""
    $shortcut.WorkingDirectory = (Join-Path $repoRoot "desktop\windows")
    if (Test-Path -LiteralPath $repoIconPath) {
        $shortcut.IconLocation = "$repoIconPath,0"
    }
    else {
        $shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
    }
    $shortcut.Save()
}

Set-Shortcut -ShortcutPath $repoShortcutPath
Set-Shortcut -ShortcutPath $shortcutPath
