[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)][string]$InputPath,
    [string]$Model = "base",
    [string]$Language = "pt",
    [string[]]$Output = @("txt", "srt", "vtt"),
    [string]$OutputDir = (Join-Path (Get-Location) "transcricoes"),
    [switch]$KeepTemp,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
$InstallRoot = Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"
$Python = Join-Path $InstallRoot ".venv\Scripts\python.exe"
$ManifestPath = Join-Path $InstallRoot "installation.json"
if (-not (Test-Path $Python) -or -not (Test-Path $ManifestPath)) {
    throw "Instalação não encontrada. Execute instalar.ps1."
}
$Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$ModelPath = Join-Path $InstallRoot "models\ggml-$Model.bin"
$Arguments = @(
    "-m", "app.cli", $InputPath,
    "--model", $Model,
    "--model-path", $ModelPath,
    "--language", $Language,
    "--output-dir", $OutputDir,
    "--whisper-cli", $Manifest.whisper_cli,
    "--output"
) + $Output
if ($KeepTemp) { $Arguments += "--keep-temp" }
if ($Quiet) { $Arguments += "--quiet" }
& $Python @Arguments
exit $LASTEXITCODE
