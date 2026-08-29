param(
    [switch]$Clean,
    [switch]$SkipExecutableBuild
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

$VersionFile = Join-Path $ProjectRoot "VERSION"
$InstallerScript = Join-Path $ProjectRoot "packaging\MeetingAssistantAI.iss"
$ExecutableBuildScript = Join-Path $ProjectRoot "scripts\build_windows_executable.ps1"
$BundleDirectory = Join-Path $ProjectRoot "dist\MeetingAssistantAI"
$BundleExecutable = Join-Path $BundleDirectory "MeetingAssistantAI.exe"
$InstallerOutputDirectory = Join-Path $ProjectRoot "dist\installer"

function Resolve-InnoSetupCompiler {
    $Command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue

    if ($null -ne $Command) {
        return $Command.Source
    }

    $Candidates = @()

    if (${env:ProgramFiles(x86)}) {
        $Candidates += Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
    }

    if ($env:ProgramFiles) {
        $Candidates += Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"
    }

    if ($env:LOCALAPPDATA) {
        $Candidates += Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
    }

    foreach ($Candidate in $Candidates) {
        if (Test-Path $Candidate) {
            return $Candidate
        }
    }

    throw (
        "Inno Setup compiler (ISCC.exe) was not found. " +
        "Install Inno Setup 6 and run this script again."
    )
}

if (-not (Test-Path $VersionFile)) {
    throw "VERSION file was not found: $VersionFile"
}

if (-not (Test-Path $InstallerScript)) {
    throw "Inno Setup script was not found: $InstallerScript"
}

if (-not (Test-Path $ExecutableBuildScript)) {
    throw "Executable build script was not found: $ExecutableBuildScript"
}

$Version = (Get-Content -Raw -Path $VersionFile).Trim()

if (
    $Version -notmatch
    '^v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$'
) {
    throw "VERSION contains an unsupported release version: $Version"
}

$InstallerOutput = Join-Path `
    $InstallerOutputDirectory `
    "MeetingAssistantAI-Setup-$Version.exe"

Push-Location $ProjectRoot

try {
    if (-not $SkipExecutableBuild) {
        Write-Host "Building production executable bundle..."

        if ($Clean) {
            & $ExecutableBuildScript -Clean
        }
        else {
            & $ExecutableBuildScript
        }
    }

    if (-not (Test-Path $BundleDirectory)) {
        throw "Executable bundle directory was not found: $BundleDirectory"
    }

    if (-not (Test-Path $BundleExecutable)) {
        throw "Executable bundle is incomplete: $BundleExecutable"
    }

    if (
        $Clean `
        -and (Test-Path $InstallerOutputDirectory)
    ) {
        Write-Host "Removing previous installer artifacts..."

        Remove-Item `
            -Recurse `
            -Force `
            $InstallerOutputDirectory
    }

    $InnoSetupCompiler = Resolve-InnoSetupCompiler

    Write-Host "Building Meeting Assistant AI installer..."
    Write-Host "Version: $Version"
    Write-Host "Compiler: $InnoSetupCompiler"

    $VersionDefine = "-dAppVersion=$Version"

    & $InnoSetupCompiler `
        $VersionDefine `
        $InstallerScript

    if ($LASTEXITCODE -ne 0) {
        throw (
            "Inno Setup compilation failed " +
            "with exit code $LASTEXITCODE."
        )
    }

    if (-not (Test-Path $InstallerOutput)) {
        throw (
            "Installer compilation completed but the expected " +
            "file was not found: $InstallerOutput"
        )
    }

    Write-Host ""
    Write-Host "Installer build completed successfully."
    Write-Host "Installer: $InstallerOutput"
}
finally {
    Pop-Location
}
