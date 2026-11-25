# Single-entry local test gate (Windows). Mirrors .github/workflows/epc-ci.yml.
# Usage:  powershell -ExecutionPolicy Bypass -File run_all_tests.ps1
$ErrorActionPreference = "Continue"
$repo = $PSScriptRoot
Set-Location $repo
$env:PYTHONIOENCODING = "utf-8"
$env:QT_QPA_PLATFORM = "offscreen"
$fail = 0

function Run-Step($name, $cmd) {
    Write-Host "== $name =="
    & $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL: $name (EXIT=$LASTEXITCODE)"
        $script:fail = 1
    }
}

Run-Step "pytest fast"  { python -m pytest tests -q -m "not slow" }
Run-Step "pytest slow"  { python -m pytest tests -q -m "slow" }
Run-Step "gui boot"     { python epc_gui\scripts\brief_start_quit.py }
Run-Step "gui smoke P0" { python epc_gui\scripts\smoke_headless.py }
Run-Step "gui smoke P1" { python epc_gui\scripts\smoke_p1.py }
Run-Step "gui smoke P2" { python epc_gui\scripts\smoke_p2.py }
Run-Step "ui interaction regression" { python epc_gui\scripts\ui_regression.py }

if ($fail -ne 0) { Write-Host "GATE FAIL"; exit 1 }
Write-Host "ALL GATES OK"
exit 0
