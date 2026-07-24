[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)][string]$InputPath,
    [string]$Model = "base",
    [string]$Language = "pt",
    [string[]]$Output = @("txt", "srt", "vtt"),
    [string]$OutputDir = (Join-Path (Get-Location) "transcricoes"),
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"),
    [switch]$KeepTemp,
    [switch]$Quiet
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"
$ModulePath = Join-Path $PSScriptRoot "TropaTranscribe.Windows.psm1"

try {
    Import-Module $ModulePath -Force
    $python = Join-Path $InstallRoot ".venv\Scripts\python.exe"
    $manifestPath = Join-Path $InstallRoot "installation.json"
    if (-not (Test-Path -LiteralPath $python -PathType Leaf) -or
        -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw (
            "Instalação não encontrada em '$InstallRoot'. " +
            "Execute primeiro .\scripts\windows\instalar.ps1."
        )
    }
    if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
        throw "Arquivo de entrada não encontrado: $InputPath"
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if (-not $manifest.whisper_cpp_version) {
        throw "installation.json é antigo ou inválido. Execute novamente instalar.ps1."
    }
    $whisperRoot = Join-Path $InstallRoot "runtime\whisper.cpp"
    $manifestCli = if ($manifest.whisper_cli) { [string]$manifest.whisper_cli } else { $null }
    $whisperCli = Find-WhisperCli -WhisperRoot $whisperRoot -ManifestCandidate $manifestCli
    $modelsRoot = if ($manifest.models_root) {
        [string]$manifest.models_root
    } else {
        Join-Path $InstallRoot "models"
    }
    $modelPath = Join-Path $modelsRoot "ggml-$Model.bin"
    if (-not (Test-Path -LiteralPath $modelPath -PathType Leaf)) {
        throw (
            "Modelo '$Model' não encontrado em '$modelsRoot'. " +
            "Execute instalar.ps1 -Model $Model."
        )
    }
    $arguments = @(
        "-m", "app.cli", $InputPath,
        "--model", $Model,
        "--model-path", $modelPath,
        "--language", $Language,
        "--output-dir", $OutputDir,
        "--ffmpeg", ([string]$manifest.ffmpeg),
        "--whisper-cli", $whisperCli,
        "--output"
    ) + $Output
    if ($KeepTemp) { $arguments += "--keep-temp" }
    if ($Quiet) { $arguments += "--quiet" }

    if (-not $Quiet) {
        Write-Host "Validando e transcrevendo localmente..."
        Write-Host "Entrada: $InputPath"
        Write-Host "Modelo: $modelPath"
        Write-Host "Saída: $OutputDir"
    }
    Invoke-CheckedNative -FilePath $python -ArgumentList $arguments `
        -Activity "Transcrição com whisper.cpp"
    if (-not $Quiet) {
        Write-Host "Transcrição concluída com sucesso. Arquivos em: $OutputDir"
    }
    exit 0
} catch {
    Write-Error "A transcrição falhou. Nenhum sucesso foi declarado. Motivo: $($_.Exception.Message)"
    exit 1
}
