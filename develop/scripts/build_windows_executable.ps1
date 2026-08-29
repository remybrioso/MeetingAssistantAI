param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$BuildRequirements = Join-Path $ProjectRoot "requirements-build.txt"
$SpecFile = Join-Path $ProjectRoot "packaging\MeetingAssistantAI.spec"
$Executable = Join-Path $ProjectRoot "dist\MeetingAssistantAI\MeetingAssistantAI.exe"

if (-not (Test-Path $Python)) {
    throw "Python executable not found in virtual environment: $Python"
}

if (-not (Test-Path $BuildRequirements)) {
    throw "requirements-build.txt was not found."
}

if (-not (Test-Path $SpecFile)) {
    throw "PyInstaller spec file was not found."
}

Push-Location $ProjectRoot

try {
    Write-Host "Installing pinned build dependencies..."

    & $Python -m pip install -r $BuildRequirements

    if ($LASTEXITCODE -ne 0) {
        throw "Build dependency installation failed."
    }

    if ($Clean) {
        Write-Host "Removing previous build artifacts..."

        $BuildDirectory = Join-Path $ProjectRoot "build"
        $DistDirectory = Join-Path $ProjectRoot "dist"

        Remove-Item `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue `
            $BuildDirectory

        Remove-Item `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue `
            $DistDirectory
    }

    Write-Host "Building Meeting Assistant AI..."

    & $Python -m PyInstaller --noconfirm --clean $SpecFile

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller finished with an error."
    }

    if (-not (Test-Path $Executable)) {
        throw "Build completed but executable was not found: $Executable"
    }

    Write-Host ""
    Write-Host "Build completed successfully."
    Write-Host "Executable: $Executable"
}
finally {
    Pop-Location
}
