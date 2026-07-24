[CmdletBinding()]
param([string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"))

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"
$ModulePath = Join-Path $PSScriptRoot "TropaTranscribe.Windows.psm1"

try {
    Import-Module $ModulePath -Force
    $manifestPath = Join-Path $InstallRoot "installation.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "installation.json não encontrado. Execute instalar.ps1."
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if (-not $manifest.app_version -or -not $manifest.models_root) {
        throw "Manifesto antigo ou incompleto. Execute novamente instalar.ps1."
    }
    $python = Join-Path $InstallRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "Python do aplicativo não encontrado. Execute novamente instalar.ps1."
    }
    $ffmpeg = Get-RequiredCommandPath "ffmpeg" `
        "Instale o FFmpeg e execute novamente instalar.ps1." `
        -Candidates @([string]$manifest.ffmpeg)
    $whisperRoot = Join-Path $InstallRoot "runtime\whisper.cpp"
    $whisperCli = Find-WhisperCli -WhisperRoot $whisperRoot `
        -ManifestCandidate ([string]$manifest.whisper_cli)
    $models = @(Get-ChildItem -LiteralPath ([string]$manifest.models_root) `
            -Filter "ggml-*.bin" -File -ErrorAction SilentlyContinue)
    if ($models.Count -eq 0) {
        throw "Nenhum modelo encontrado em '$($manifest.models_root)'."
    }
    foreach ($modelFile in $models) {
        $name = $modelFile.BaseName.Substring("ggml-".Length)
        Invoke-CheckedNative -FilePath $python -ArgumentList @(
            (Join-Path ([string]$manifest.project_root) "tools\verify_model.py"),
            $name,
            $modelFile.FullName
        ) -Activity "Validação de integridade do modelo $name"
    }
    Invoke-CheckedNative -FilePath $ffmpeg -ArgumentList @("-version") `
        -Activity "Teste do FFmpeg" -CaptureOutput | Out-Null
    Invoke-CheckedNative -FilePath $whisperCli -ArgumentList @("--help") `
        -Activity "Teste do whisper-cli" -CaptureOutput | Out-Null

    $driveName = [IO.Path]::GetPathRoot($InstallRoot).TrimEnd(":\")
    $drive = Get-PSDrive -Name $driveName
    $memory = Get-CimInstance Win32_ComputerSystem
    Write-Host "Tropa Transcribe Local:" $manifest.app_version
    Write-Host "Instalado em:" $manifest.installed_at
    Write-Host "FFmpeg:" $ffmpeg
    Write-Host "whisper-cli:" $whisperCli
    Write-Host "Modelos válidos:" ($models.Name -join ", ")
    Write-Host "Visual Studio:" $manifest.environment.visual_studio
    Write-Host "Espaço livre:" ([math]::Round($drive.Free / 1GB, 1)) "GiB"
    Write-Host "Memória física:" ([math]::Round($memory.TotalPhysicalMemory / 1GB, 1)) "GiB"
    Write-Host ""
    Write-Host "Verificação aprovada. O ambiente está pronto para um teste real."
    exit 0
} catch {
    Write-Error (
        "Verificação reprovada: $($_.Exception.Message)`n" +
        "Leia docs\instalacao-windows.md antes de tentar transcrever."
    )
    exit 1
}
