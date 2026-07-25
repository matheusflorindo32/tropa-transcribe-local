[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Executable,
    [string]$Model = "small",
    [string]$WorkDirectory = ""
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw "Este teste exige Windows."
}
$exe = (Resolve-Path -LiteralPath $Executable).Path
$root = if ($WorkDirectory) {
    [System.IO.Path]::GetFullPath($WorkDirectory)
} else {
    Join-Path ([System.IO.Path]::GetTempPath()) `
        ("tropa-packaged-smoke-" + [guid]::NewGuid().ToString("N"))
}
New-Item -ItemType Directory -Force -Path $root | Out-Null
$wav = Join-Path $root "fala sintética.wav"
$ogg = Join-Path $root "fala sintética.ogg"
$output = Join-Path $root "saídas"
New-Item -ItemType Directory -Force -Path $output | Out-Null

Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $speaker.SetOutputToWaveFile($wav)
    $speaker.Speak("Este é um teste de transcrição local e privada.")
} finally {
    $speaker.Dispose()
}

$runtime = Join-Path $env:LOCALAPPDATA `
    "TropaTranscribeLocal\runtime-v2\ffmpeg\n8.1.2-31-g8c9502e9b0\bin\ffmpeg.exe"
if (-not (Test-Path -LiteralPath $runtime -PathType Leaf)) {
    throw "FFmpeg provisionado não localizado: $runtime"
}
& $runtime -nostdin -hide_banner -loglevel error -y -i $wav -c:a libopus $ogg
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $ogg -PathType Leaf)) {
    throw "Não foi possível produzir o OGG/Opus sintético."
}

$arguments = @(
    "--headless-transcribe",
    ('"{0}"' -f $ogg),
    "--model", $Model,
    "--language", "pt",
    "--output", "txt", "srt", "vtt", "json",
    "--output-dir", ('"{0}"' -f $output),
    "--quiet"
)
$process = Start-Process -FilePath $exe -ArgumentList $arguments `
    -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "O EXE empacotado terminou com código $($process.ExitCode)."
}
foreach ($extension in @("txt", "srt", "vtt", "json")) {
    $file = Join-Path $output ("fala sintética." + $extension)
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Saída ausente: $file"
    }
    if ((Get-Item -LiteralPath $file).Length -eq 0) {
        throw "Saída vazia: $file"
    }
}
Write-Host "Smoke aprovado: EXE -> OGG/Opus sintético -> TXT/SRT/VTT/JSON."
Write-Host "Evidência local:" $root
