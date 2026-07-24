[CmdletBinding()]
param(
    [switch]$BuildInstaller,
    [string]$PythonPath = ""
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
    $python = if ($PythonPath) {
        if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
            throw "PythonPath não aponta para um executável: $PythonPath"
        }
        (Resolve-Path -LiteralPath $PythonPath).Path
    } else {
        Get-RequiredCommandPath "python" "Instale Python 3.11 ou 3.12 para construir."
    }
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
    Invoke-CheckedNative -FilePath $python -ArgumentList @(
        (Join-Path $ProjectRoot "tools\generate_supply_chain.py"),
        "--components", (Join-Path $ProjectRoot "packaging\components.json"),
        "--artifact-dir", (Join-Path $ProjectRoot "dist\TropaTranscribeLocal"),
        "--output-dir", (Join-Path $ProjectRoot "dist\manifest")
    ) -Activity "Geração do SBOM e hashes SHA-256"
    Write-Host "SBOM e hashes criados em dist\manifest."

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
        $innoRegistry = Get-ItemProperty `
            "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 7_is1" `
            -ErrorAction SilentlyContinue
        $isccVersion = if ($innoRegistry.DisplayVersion) {
            $innoRegistry.DisplayVersion
        } else {
            (Get-Item -LiteralPath $iscc).VersionInfo.ProductVersion
        }
        if (-not $isccVersion -or ([version]$isccVersion -lt [version]"7.0.2")) {
            throw "Inno Setup 7.0.2 ou superior é obrigatório; encontrado: $isccVersion"
        }
        Write-Host "Inno Setup validado:" $isccVersion "-" $iscc
        Invoke-CheckedNative -FilePath $iscc -ArgumentList @(
            (Join-Path $ProjectRoot "packaging\windows\installer.iss")
        ) -Activity "Compilação do instalador Inno Setup"
        $installer = Join-Path $ProjectRoot `
            "dist\installer\TropaTranscribeLocal-0.3.1-alpha-setup.exe"
        if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) {
            throw "ISCC terminou sem produzir o instalador experimental esperado."
        }
        $installerHash = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash
        $installerSignature = (Get-AuthenticodeSignature -LiteralPath $installer).Status
        Write-Host "Instalador experimental local:" $installer
        Write-Host "SHA-256:" $installerHash
        Write-Host "Assinatura Authenticode:" $installerSignature `
            "(esperado NotSigned nesta fase; não publicar)."
    } else {
        Write-Host "Inno Setup não executado. Use -BuildInstaller somente para validação local."
    }
} catch {
    Write-Error "Empacotamento reprovado: $($_.Exception.Message)"
    exit 1
}
