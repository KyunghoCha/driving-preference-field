$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$projectRoot = $repoRoot
$defaultPythonExe = Join-Path $env:USERPROFILE "anaconda3\envs\local-reference-path-cost\python.exe"
$legacyPythonExe = Join-Path $env:USERPROFILE "anaconda3\envs\driving-preference-field\python.exe"
if ($env:LRPC_PYTHON_EXE) {
    $pythonExe = $env:LRPC_PYTHON_EXE
}
elseif (Test-Path -LiteralPath $defaultPythonExe) {
    $pythonExe = $defaultPythonExe
}
elseif (Test-Path -LiteralPath $legacyPythonExe) {
    $pythonExe = $legacyPythonExe
}
else {
    $pythonExe = $defaultPythonExe
}
$casePath = if ($env:LRPC_CASE_PATH) { $env:LRPC_CASE_PATH } else { "cases/toy/straight_corridor.yaml" }
$desktop = [Environment]::GetFolderPath("Desktop")
$logPath = Join-Path $desktop "Local Reference Path Cost Lab.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $logPath -Value "[$timestamp] $Message" -Encoding UTF8
}

function Show-LaunchError {
    param([string]$Message)
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        "$Message`r`n`r`nLog: $logPath",
        "Local Reference Path Cost Lab",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
}

function New-ProcessStartInfo {
    param(
        [string]$FilePath,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [switch]$RedirectOutput,
        [hashtable]$EnvironmentOverrides
    )

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $FilePath
    $startInfo.Arguments = $Arguments
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true

    if ($RedirectOutput) {
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
    }

    foreach ($entry in $EnvironmentOverrides.GetEnumerator()) {
        $startInfo.EnvironmentVariables[$entry.Key] = [string]$entry.Value
    }

    return $startInfo
}

function Invoke-Process {
    param(
        [string]$FilePath,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [hashtable]$EnvironmentOverrides
    )

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = New-ProcessStartInfo `
        -FilePath $FilePath `
        -Arguments $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectOutput `
        -EnvironmentOverrides $EnvironmentOverrides

    if (-not $process.Start()) {
        throw "프로세스를 시작하지 못했습니다: $FilePath"
    }

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    return [PSCustomObject]@{
        ExitCode = $process.ExitCode
        StdOut = $stdout
        StdErr = $stderr
    }
}

function Start-DetachedProcess {
    param(
        [string]$FilePath,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [hashtable]$EnvironmentOverrides
    )

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = New-ProcessStartInfo `
        -FilePath $FilePath `
        -Arguments $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -EnvironmentOverrides $EnvironmentOverrides

    if (-not $process.Start()) {
        throw "프로세스를 시작하지 못했습니다: $FilePath"
    }

    return $process
}

try {
    Set-Content -LiteralPath $logPath -Value "" -Encoding UTF8
    Write-Log "Launcher start"
    Write-Log "PROJECT_ROOT=$projectRoot"
    Write-Log "PYTHON_EXE=$pythonExe"

    if (-not (Test-Path -LiteralPath $projectRoot)) {
        throw "프로젝트 경로를 찾지 못했습니다: $projectRoot"
    }

    if (-not (Test-Path -LiteralPath $pythonExe)) {
        throw "파이썬 실행 파일을 찾지 못했습니다: $pythonExe"
    }

    $caseFullPath = Join-Path $projectRoot $casePath
    if (-not (Test-Path -LiteralPath $caseFullPath)) {
        throw "케이스 파일을 찾지 못했습니다: $caseFullPath"
    }

    $pythonPath = Join-Path $projectRoot "src"
    $environmentOverrides = @{
        "PYTHONPATH" = $pythonPath
        "PYTHONUTF8" = "1"
        "PYTHONIOENCODING" = "utf-8"
        "MPLBACKEND" = "Agg"
    }

    Write-Log "PYTHONPATH=$pythonPath"
    Write-Log "CASE_PATH=$caseFullPath"

    $probePath = Join-Path $env:TEMP "local_reference_path_cost_probe.py"
    $probeScript = @"
import sys
sys.path.insert(0, r"$pythonPath")
import matplotlib
import numpy
from PyQt6.QtWidgets import QApplication
import local_reference_path_cost
print(f"PROBE_PYTHON={sys.version.split()[0]}")
print(f"PROBE_NUMPY={numpy.__version__}")
print(f"PROBE_MPL={matplotlib.__version__}")
print("PROBE_OK")
"@
    Set-Content -LiteralPath $probePath -Value $probeScript -Encoding UTF8

    $probeResult = Invoke-Process `
        -FilePath $pythonExe `
        -Arguments "`"$probePath`"" `
        -WorkingDirectory $projectRoot `
        -EnvironmentOverrides $environmentOverrides

    if ($probeResult.StdOut) {
        foreach ($line in ($probeResult.StdOut -split "`r?`n")) {
            if ($line) {
                Write-Log "PROBE_OUT: $line"
            }
        }
    }

    if ($probeResult.StdErr) {
        foreach ($line in ($probeResult.StdErr -split "`r?`n")) {
            if ($line) {
                Write-Log "PROBE_ERR: $line"
            }
        }
    }

    if ($probeResult.ExitCode -ne 0) {
        throw "환경 probe가 실패했습니다. numpy/matplotlib/PyQt6/project import를 확인하세요. Windows known-good NumPy: 1.26.4. 종료 코드: $($probeResult.ExitCode)"
    }

    if ($probeResult.StdOut -notmatch "PROBE_OK") {
        throw "파이썬 초기 확인 출력이 예상과 다릅니다."
    }

    Remove-Item -LiteralPath $probePath -Force -ErrorAction SilentlyContinue

    $launchArguments = "-m local_reference_path_cost parameter-lab --case $casePath"
    Write-Log "Launching Parameter Lab"
    $uiProcess = Start-DetachedProcess `
        -FilePath $pythonExe `
        -Arguments $launchArguments `
        -WorkingDirectory $projectRoot `
        -EnvironmentOverrides $environmentOverrides

    Start-Sleep -Milliseconds 1500

    if ($uiProcess.HasExited) {
        throw "실행 직후 종료되었습니다. 종료 코드: $($uiProcess.ExitCode)"
    }

    Write-Log "Process started. PID=$($uiProcess.Id)"
}
catch {
    $message = $_.Exception.Message
    Write-Log "ERROR: $message"
    Show-LaunchError $message
}
