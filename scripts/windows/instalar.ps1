[CmdletBinding()]
param(
    [ValidateSet("tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3", "large-v3-turbo")]
    [string]$Model = "base",
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"),
    [switch]$SkipModel,
    [switch]$ForceRebuild
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$WhisperVersion = "v1.9.1"
$AppVersion = "0.2.0-beta"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$RuntimeRoot = Join-Path $InstallRoot "runtime"
$WhisperRoot = Join-Path $RuntimeRoot "whisper.cpp"
$VenvRoot = Join-Path $InstallRoot ".venv"
$ModelsRoot = Join-Path $InstallRoot "models"
$ManifestPath = Join-Path $InstallRoot "installation.json"
$ModulePath = Join-Path $PSScriptRoot "TropaTranscribe.Windows.psm1"

function Get-FirstLine {
    param([string]$FilePath, [string[]]$Arguments, [string]$Activity)
    $lines = @(Invoke-CheckedNative -FilePath $FilePath -ArgumentList $Arguments `
            -Activity $Activity -CaptureOutput)
    return ($lines | Where-Object { $_ } | Select-Object -First 1).ToString().Trim()
}

try {
    Import-Module $ModulePath -Force
    Write-Host ""
    Write-Host "Tropa Transcribe Local $AppVersion — estabilização Windows"
    Write-Host "Destino: $InstallRoot"
    Write-Host ""

    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        throw "Este instalador é exclusivo para Windows."
    }
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        throw "PowerShell 5.1 ou superior é necessário."
    }

    $git = Get-RequiredCommandPath "git" `
        "Instale pelo site oficial: https://git-scm.com/download/win"
    $systemPython = Get-RequiredCommandPath "python" `
        "Instale Python 3.11 ou 3.12: https://www.python.org/downloads/windows/"

    Write-Host "[1/7] Localizando Visual Studio Build Tools 2022..."
    $visualStudio = Get-VisualStudioInstallation
    Import-VisualStudioEnvironment -VsDevCmd $visualStudio.VsDevCmd
    $compiler = Get-RequiredCommandPath "cl.exe" "Repare o componente C++ do Visual Studio."
    Write-Host "      Visual Studio $($visualStudio.Version) encontrado."

    $cmake = Get-RequiredCommandPath "cmake" `
        "Instale pelo site oficial: https://cmake.org/download/" `
        -Candidates @(
            (Join-Path $env:ProgramFiles "CMake\bin\cmake.exe"),
            (Join-Path $visualStudio.InstallationPath `
                "Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe")
        )
    $wingetRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    $wingetFfmpeg = @()
    if (Test-Path -LiteralPath $wingetRoot -PathType Container) {
        $wingetFfmpeg = @(
            Get-ChildItem -LiteralPath $wingetRoot -Directory -Filter "*FFmpeg*" |
                Get-ChildItem -Recurse -File -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName
        )
    }
    $ffmpeg = Get-RequiredCommandPath "ffmpeg" `
        "Instale uma distribuição confiável e confirme com: ffmpeg -version" `
        -Candidates $wingetFfmpeg

    New-Item -ItemType Directory -Force -Path $InstallRoot, $RuntimeRoot, $ModelsRoot |
        Out-Null

    Write-Host "[2/7] Preparando whisper.cpp $WhisperVersion..."
    if (-not (Test-Path -LiteralPath (Join-Path $WhisperRoot ".git"))) {
        Invoke-CheckedNative -FilePath $git -ArgumentList @(
            "clone", "--branch", $WhisperVersion, "--depth", "1",
            "https://github.com/ggml-org/whisper.cpp.git", $WhisperRoot
        ) -Activity "Clone do whisper.cpp"
    } else {
        $remote = Get-FirstLine $git @("-C", $WhisperRoot, "remote", "get-url", "origin") `
            "Validação do repositório whisper.cpp"
        if ($remote -notmatch "^https://github\.com/ggml-org/whisper\.cpp(?:\.git)?$") {
            throw "O runtime existente possui origem inesperada: $remote"
        }
        $dirty = @(
            Invoke-CheckedNative -FilePath $git -ArgumentList @(
                "-C", $WhisperRoot, "status", "--porcelain", "--untracked-files=no"
            ) -Activity "Validação do runtime existente" -CaptureOutput
        )
        if ($dirty.Count -gt 0) {
            throw "O runtime whisper.cpp possui alterações locais. Não serão sobrescritas."
        }
        Invoke-CheckedNative -FilePath $git -ArgumentList @(
            "-C", $WhisperRoot, "fetch", "--depth", "1", "origin", "tag", $WhisperVersion
        ) -Activity "Atualização do tag fixado do whisper.cpp"
        Invoke-CheckedNative -FilePath $git -ArgumentList @(
            "-C", $WhisperRoot, "checkout", "--detach", $WhisperVersion
        ) -Activity "Seleção do whisper.cpp $WhisperVersion"
    }

    Write-Host "[3/7] Configurando compilação Visual Studio x64..."
    $buildRoot = Join-Path $WhisperRoot "build"
    $cachePath = Join-Path $buildRoot "CMakeCache.txt"
    $resetBuild = $ForceRebuild
    if (Test-Path -LiteralPath $cachePath) {
        $generatorLine = Get-Content -LiteralPath $cachePath |
            Where-Object { $_ -like "CMAKE_GENERATOR:INTERNAL=*" } |
            Select-Object -First 1
        $instanceLine = Get-Content -LiteralPath $cachePath |
            Where-Object { $_ -like "CMAKE_GENERATOR_INSTANCE:INTERNAL=*" } |
            Select-Object -First 1
        $instanceMismatch = $false
        if ($instanceLine) {
            $cachedInstance = $instanceLine.Substring(
                "CMAKE_GENERATOR_INSTANCE:INTERNAL=".Length
            )
            $normalizedCached = [IO.Path]::GetFullPath($cachedInstance).TrimEnd("\")
            $normalizedExpected = [IO.Path]::GetFullPath(
                $visualStudio.GeneratorInstance
            ).TrimEnd("\")
            $instanceMismatch = -not $normalizedCached.Equals(
                $normalizedExpected,
                [StringComparison]::OrdinalIgnoreCase
            )
        }
        if ($generatorLine -ne "CMAKE_GENERATOR:INTERNAL=Visual Studio 17 2022" -or
            $instanceMismatch) {
            $resetBuild = $true
        }
    }
    if ($resetBuild -and (Test-Path -LiteralPath $buildRoot)) {
        $resolvedBuild = (Resolve-Path -LiteralPath $buildRoot).Path
        $resolvedWhisper = (Resolve-Path -LiteralPath $WhisperRoot).Path
        if (-not $resolvedBuild.StartsWith("$resolvedWhisper\", [StringComparison]::OrdinalIgnoreCase)) {
            throw "Recusa de segurança: diretório de build fora do runtime gerenciado."
        }
        Write-Host "      Cache incompatível encontrado; recriando somente '$resolvedBuild'."
        Remove-Item -LiteralPath $resolvedBuild -Recurse -Force
    }
    Invoke-CheckedNative -FilePath $cmake -ArgumentList @(
        "-S", $WhisperRoot,
        "-B", $buildRoot,
        "-G", "Visual Studio 17 2022",
        "-A", "x64",
        "-DCMAKE_GENERATOR_INSTANCE=$($visualStudio.GeneratorInstance)",
        "-DWHISPER_BUILD_TESTS=OFF",
        "-DWHISPER_BUILD_EXAMPLES=ON"
    ) -Activity "Configuração CMake"

    Write-Host "[4/7] Compilando whisper-cli em Release..."
    Invoke-CheckedNative -FilePath $cmake -ArgumentList @(
        "--build", $buildRoot, "--config", "Release", "--parallel"
    ) -Activity "Compilação do whisper.cpp"
    $whisperCli = Find-WhisperCli -WhisperRoot $WhisperRoot
    Invoke-CheckedNative -FilePath $whisperCli -ArgumentList @("--help") `
        -Activity "Teste do whisper-cli"

    Write-Host "[5/7] Preparando ambiente Python..."
    $venvPython = Join-Path $VenvRoot "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        Invoke-CheckedNative -FilePath $systemPython -ArgumentList @("-m", "venv", $VenvRoot) `
            -Activity "Criação do ambiente virtual"
    }
    Invoke-CheckedNative -FilePath $venvPython -ArgumentList @(
        "-m", "pip", "install", "--upgrade", "pip>=26.1.2", "setuptools>=83.0.0"
    ) -Activity "Atualização das ferramentas Python"
    Invoke-CheckedNative -FilePath $venvPython -ArgumentList @(
        "-m", "pip", "install", "--editable", $ProjectRoot
    ) -Activity "Instalação do Tropa Transcribe Local"

    $modelPath = Join-Path $ModelsRoot "ggml-$Model.bin"
    if (-not $SkipModel) {
        Write-Host "[6/7] Validando ou baixando o modelo '$Model'..."
        Invoke-CheckedNative -FilePath $venvPython -ArgumentList @(
            (Join-Path $ProjectRoot "tools\download_model.py"),
            $Model,
            "--directory", $ModelsRoot
        ) -Activity "Preparação do modelo $Model"
    } else {
        Write-Host "[6/7] Download do modelo ignorado por solicitação (-SkipModel)."
        $modelPath = $null
    }

    Write-Host "[7/7] Registrando versões e ambiente..."
    $modelRecord = $null
    if ($modelPath -and (Test-Path -LiteralPath $modelPath -PathType Leaf)) {
        $modelRecord = @{
            name = $Model
            path = (Resolve-Path -LiteralPath $modelPath).Path
            size_bytes = (Get-Item -LiteralPath $modelPath).Length
            sha256 = (Get-FileHash -LiteralPath $modelPath -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $manifest = @{
        schema_version = 2
        app_version = $AppVersion
        whisper_cpp_version = $WhisperVersion
        whisper_cli = $whisperCli
        ffmpeg = $ffmpeg
        project_root = $ProjectRoot
        install_root = (Resolve-Path -LiteralPath $InstallRoot).Path
        models_root = (Resolve-Path -LiteralPath $ModelsRoot).Path
        default_model = $Model
        model = $modelRecord
        installed_at = (Get-Date).ToUniversalTime().ToString("o")
        environment = @{
            os = [Environment]::OSVersion.VersionString
            architecture = [Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
            powershell = $PSVersionTable.PSVersion.ToString()
            python = (Get-FirstLine $venvPython @("--version") "Leitura da versão do Python")
            cmake = (Get-FirstLine $cmake @("--version") "Leitura da versão do CMake")
            ffmpeg = (Get-FirstLine $ffmpeg @("-version") "Leitura da versão do FFmpeg")
            visual_studio = $visualStudio.Version
            visual_studio_path = $visualStudio.InstallationPath
            compiler = $compiler
            vscmd = $env:VSCMD_VER
        }
    }
    Save-AtomicUtf8Json -Data $manifest -Path $ManifestPath

    Write-Host ""
    if ($SkipModel) {
        Write-Host "Runtime instalado e verificado. Nenhum modelo foi preparado."
        Write-Host "Para concluir, execute novamente sem -SkipModel."
    } else {
        Write-Host "Instalação concluída e verificada com o modelo '$Model'."
    }
    Write-Host "Próximo passo: .\scripts\windows\verificar.ps1"
} catch {
    Write-Error (
        "A instalação NÃO foi concluída. Nenhum sucesso foi registrado.`n" +
        "Motivo: $($_.Exception.Message)"
    )
    exit 1
}
