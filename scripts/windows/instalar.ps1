[CmdletBinding()]
param(
    [ValidateSet("tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3", "large-v3-turbo")]
    [string]$Model = "base",
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"),
    [switch]$SkipModel
)

$ErrorActionPreference = "Stop"
$WhisperVersion = "v1.9.1"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$RuntimeRoot = Join-Path $InstallRoot "runtime"
$WhisperRoot = Join-Path $RuntimeRoot "whisper.cpp"
$VenvRoot = Join-Path $InstallRoot ".venv"
$ModelsRoot = Join-Path $InstallRoot "models"

function Require-Command {
    param([string]$Name, [string]$Guidance)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name não encontrado. $Guidance"
    }
}

Write-Host "Tropa Transcribe Local — instalação local"
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw "Este instalador é exclusivo para Windows."
}
if ($PSVersionTable.PSVersion.Major -lt 5) {
    throw "PowerShell 5.1 ou superior é necessário."
}
Require-Command "git" "Instale pelo site oficial: https://git-scm.com/download/win"
Require-Command "cmake" "Instale pelo site oficial: https://cmake.org/download/"
Require-Command "ffmpeg" "Instale uma distribuição compatível e confirme com: ffmpeg -version"
Require-Command "python" "Instale Python 3.11 ou 3.12: https://www.python.org/downloads/windows/"

$Compiler = Get-Command "cl.exe" -ErrorAction SilentlyContinue
if (-not $Compiler) {
    $Compiler = Get-Command "g++.exe" -ErrorAction SilentlyContinue
}
if (-not $Compiler) {
    throw "Compilador C++ não encontrado. Instale Visual Studio Build Tools com 'Desktop development with C++'."
}

New-Item -ItemType Directory -Force -Path $RuntimeRoot, $ModelsRoot | Out-Null
if (-not (Test-Path (Join-Path $WhisperRoot ".git"))) {
    git clone --branch $WhisperVersion --depth 1 https://github.com/ggml-org/whisper.cpp.git $WhisperRoot
} else {
    $Current = git -C $WhisperRoot describe --tags --exact-match 2>$null
    if ($Current -ne $WhisperVersion) {
        Write-Warning "whisper.cpp existente em '$Current'. A versão não foi alterada automaticamente."
    }
}

$BuildRoot = Join-Path $WhisperRoot "build"
cmake -S $WhisperRoot -B $BuildRoot -DCMAKE_BUILD_TYPE=Release
cmake --build $BuildRoot --config Release --parallel
$Candidates = @(
    (Join-Path $BuildRoot "bin\Release\whisper-cli.exe"),
    (Join-Path $BuildRoot "bin\whisper-cli.exe")
)
$WhisperCli = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $WhisperCli) {
    throw "A compilação terminou sem produzir whisper-cli.exe."
}

if (-not (Test-Path (Join-Path $VenvRoot "Scripts\python.exe"))) {
    python -m venv $VenvRoot
}
$Python = Join-Path $VenvRoot "Scripts\python.exe"
& $Python -m pip install --upgrade "pip>=26.1.2" "setuptools>=83.0.0"
& $Python -m pip install --editable $ProjectRoot
if (-not $SkipModel) {
    & $Python (Join-Path $ProjectRoot "tools\download_model.py") $Model --directory $ModelsRoot
}

$Manifest = @{
    whisper_cpp_version = $WhisperVersion
    whisper_cli = $WhisperCli
    ffmpeg = (Get-Command ffmpeg).Source
    installed_at = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json
$Manifest | Set-Content -LiteralPath (Join-Path $InstallRoot "installation.json") -Encoding UTF8
Write-Host "Instalação concluída. Execute scripts\windows\verificar.ps1."
