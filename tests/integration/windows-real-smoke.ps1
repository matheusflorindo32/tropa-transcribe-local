[CmdletBinding()]
param(
    [ValidateSet("tiny", "base", "small", "medium", "large-v3-turbo")]
    [string]$Model = "small",
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"),
    [switch]$KeepArtifacts
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Workspace = Join-Path $env:TEMP "tropa-transcribe-integration-$([Guid]::NewGuid().ToString('N'))"
$InputPath = Join-Path $Workspace "fala-artificial.wav"
$OutputDir = Join-Path $Workspace "saidas"

try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        throw "Este teste real usa a voz sintética do Windows."
    }
    New-Item -ItemType Directory -Force -Path $Workspace, $OutputDir | Out-Null
    Add-Type -AssemblyName System.Speech
    $synthesizer = [System.Speech.Synthesis.SpeechSynthesizer]::new()
    try {
        $portugueseVoice = $synthesizer.GetInstalledVoices() |
            Where-Object { $_.VoiceInfo.Culture.Name -like "pt-*" } |
            Select-Object -First 1
        if ($portugueseVoice) {
            $synthesizer.SelectVoice($portugueseVoice.VoiceInfo.Name)
        }
        $synthesizer.SetOutputToWaveFile($InputPath)
        $synthesizer.Speak(
            "Este é um teste de integração do Tropa Transcribe Local no Windows."
        )
    } finally {
        $synthesizer.Dispose()
    }
    if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
        throw "A voz sintética não gerou o WAV de entrada."
    }

    & (Join-Path $ProjectRoot "scripts\windows\transcrever.ps1") `
        -InputPath $InputPath `
        -Model $Model `
        -Language "pt" `
        -Output @("txt", "srt", "vtt") `
        -OutputDir $OutputDir `
        -InstallRoot $InstallRoot `
        -Quiet
    if ($LASTEXITCODE -ne 0) {
        throw "transcrever.ps1 retornou código $LASTEXITCODE."
    }
    foreach ($extension in @("txt", "srt", "vtt")) {
        $generated = @(
            Get-ChildItem -LiteralPath $OutputDir -Filter "*.$extension" -File
        )
        if ($generated.Count -ne 1 -or $generated[0].Length -eq 0) {
            throw "Saída .$extension ausente, duplicada ou vazia."
        }
    }
    Write-Host "Teste real aprovado: voz sintética -> FFmpeg -> whisper.cpp -> TXT/SRT/VTT."
    exit 0
} catch {
    Write-Error "Teste real reprovado. Artefatos: $Workspace. Motivo: $($_.Exception.Message)"
    $KeepArtifacts = $true
    exit 1
} finally {
    if (-not $KeepArtifacts -and (Test-Path -LiteralPath $Workspace)) {
        Remove-Item -LiteralPath $Workspace -Recurse -Force
    }
}
