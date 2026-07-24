[CmdletBinding()]
param([string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"))

$ManifestPath = Join-Path $InstallRoot "installation.json"
$Manifest = if (Test-Path $ManifestPath) {
    Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
} else {
    $null
}
$FFmpeg = Get-Command "ffmpeg" -ErrorAction SilentlyContinue
$WhisperCli = if ($Manifest -and (Test-Path $Manifest.whisper_cli)) { $Manifest.whisper_cli } else { $null }
$Models = @(Get-ChildItem -LiteralPath (Join-Path $InstallRoot "models") -Filter "ggml-*.bin" -ErrorAction SilentlyContinue)
$Drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($InstallRoot).TrimEnd(":\"))
$Memory = Get-CimInstance Win32_ComputerSystem

$FFmpegDisplay = if ($FFmpeg) { $FFmpeg.Source } else { "NÃO ENCONTRADO" }
$WhisperDisplay = if ($WhisperCli) { $WhisperCli } else { "NÃO ENCONTRADO" }
Write-Host "FFmpeg:" $FFmpegDisplay
Write-Host "whisper-cli:" $WhisperDisplay
Write-Host "Modelos:" ($(if ($Models.Count) { $Models.Name -join ", " } else { "NENHUM" }))
Write-Host "Espaço livre:" ([math]::Round($Drive.Free / 1GB, 1)) "GiB"
Write-Host "Memória física:" ([math]::Round($Memory.TotalPhysicalMemory / 1GB, 1)) "GiB"
Write-Host "Diretório:" $InstallRoot

if (-not $FFmpeg -or -not $WhisperCli -or $Models.Count -eq 0) {
    Write-Warning "Ambiente incompleto. Consulte docs/instalacao-windows.md."
    exit 1
}
& $WhisperCli --help *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "whisper-cli foi encontrado, mas o teste --help falhou."
    exit 2
}
Write-Host "Verificação básica aprovada."
