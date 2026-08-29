param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (
    Split-Path
    -Parent
    $PSScriptRoot
)

$Python = Join-Path (
    $ProjectRoot
) ".venv\Scripts\python.exe"

$BuildRequirements = Join-Path (
    $ProjectRoot
) "requirements-build.txt"

$SpecFile = Join-Path (
    $ProjectRoot
) "packaging\MeetingAssistantAI.spec"

$Executable = Join-Path (
    $ProjectRoot
) "dist\MeetingAssistantAI\MeetingAssistantAI.exe"

if (-not (Test-Path $Python)) {
    throw (
        "No se encontró el Python del entorno virtual: "
        + $Python
    )
}

if (-not (Test-Path $BuildRequirements)) {
    throw (
        "No se encontró requirements-build.txt."
    )
}

if (-not (Test-Path $SpecFile)) {
    throw (
        "No se encontró el contrato PyInstaller."
    )
}

Push-Location $ProjectRoot

try {
    Write-Host (
        "Installing pinned build dependencies..."
    )

    & $Python -m pip install `
        -r $BuildRequirements

    if ($LASTEXITCODE -ne 0) {
        throw (
            "Falló la instalación de dependencias de build."
        )
    }

    if ($Clean) {
        Write-Host (
            "Removing previous build artifacts..."
        )

        Remove-Item `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue `
            (Join-Path $ProjectRoot "build")

        Remove-Item `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue `
            (Join-Path $ProjectRoot "dist")
    }

    Write-Host (
        "Building Meeting Assistant AI..."
    )

    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        $SpecFile

    if ($LASTEXITCODE -ne 0) {
        throw (
            "PyInstaller terminó con error."
        )
    }

    if (-not (Test-Path $Executable)) {
        throw (
            "El build terminó pero no se encontró: "
            + $Executable
        )
    }

    Write-Host ""
    Write-Host (
        "Build completed successfully."
    )
    Write-Host (
        "Executable: "
        + $Executable
    )
}
finally {
    Pop-Location
}
