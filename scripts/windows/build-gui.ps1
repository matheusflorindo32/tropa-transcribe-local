[CmdletBinding()]
param(
    [switch]$BuildInstaller
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ModulePath = Join-Path $PSScriptRoot "TropaTranscribe.Windows.psm1"

try {
    Import-Module $ModulePath -Force
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        throw "O pacote Windows precisa ser construído no Windows."
    }
    $python = Get-RequiredCommandPath "python" "Instale Python 3.11 ou 3.12."
    Invoke-CheckedNative -FilePath $python -ArgumentList @(
        "-m", "pip", "install", "--editable", "$ProjectRoot[gui,packaging]"
    ) -Activity "Instalação das dependências de empacotamento"
    Invoke-CheckedNative -FilePath $python -ArgumentList @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath", (Join-Path $ProjectRoot "dist"),
        "--workpath", (Join-Path $ProjectRoot "build\pyinstaller"),
        (Join-Path $ProjectRoot "packaging\windows\tropa-transcribe-local.spec")
    ) -Activity "Build onedir da GUI"

    $guiExecutable = Join-Path $ProjectRoot "dist\TropaTranscribeLocal\TropaTranscribeLocal.exe"
    if (-not (Test-Path -LiteralPath $guiExecutable -PathType Leaf)) {
        throw "PyInstaller terminou sem produzir TropaTranscribeLocal.exe."
    }
    Write-Host "Bundle GUI criado para validação local: $guiExecutable"

    if ($BuildInstaller) {
        $programFilesX86 = ${env:ProgramFiles(x86)}
        if (-not $programFilesX86) { $programFilesX86 = $env:ProgramFiles }
        $isccCandidates = @(
            (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 7\ISCC.exe"),
            (Join-Path $env:ProgramFiles "Inno Setup 7\ISCC.exe"),
            (Join-Path $programFilesX86 "Inno Setup 6\ISCC.exe")
        )
        $iscc = $isccCandidates |
            Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
            Select-Object -First 1
        if (-not $iscc) {
            throw "ISCC.exe não encontrado. Instale Inno Setup 7 e tente novamente."
        }
        Invoke-CheckedNative -FilePath $iscc -ArgumentList @(
            (Join-Path $ProjectRoot "packaging\windows\installer.iss")
        ) -Activity "Compilação do instalador Inno Setup"
        Write-Host "Instalador criado apenas para validação local em dist\installer."
    } else {
        Write-Host "Inno Setup não executado. Use -BuildInstaller somente para validação local."
    }
} catch {
    Write-Error "Empacotamento reprovado: $($_.Exception.Message)"
    exit 1
}
