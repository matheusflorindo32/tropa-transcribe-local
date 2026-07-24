Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

function Invoke-CheckedNative {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [Parameter(Mandatory)][string]$Activity,
        [switch]$CaptureOutput
    )

    if ($CaptureOutput) {
        $output = & $FilePath @ArgumentList 2>&1
    } else {
        & $FilePath @ArgumentList
        $output = $null
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        $detail = if ($CaptureOutput -and $output) {
            ($output | Select-Object -Last 3) -join [Environment]::NewLine
        } else {
            "Consulte as mensagens exibidas acima."
        }
        throw "$Activity falhou (código $exitCode). $detail"
    }
    if ($CaptureOutput) {
        return $output
    }
}

function Get-RequiredCommandPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Guidance,
        [string[]]$Candidates = @()
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    $candidate = $Candidates |
        Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } |
        Select-Object -First 1
    if ($candidate) {
        return (Resolve-Path -LiteralPath $candidate).Path
    }
    throw "$Name não encontrado. $Guidance"
}

function Get-VisualStudioInstallation {
    [CmdletBinding()]
    param()

    $programFilesX86 = ${env:ProgramFiles(x86)}
    if (-not $programFilesX86) {
        $programFilesX86 = $env:ProgramFiles
    }
    $vswhere = Join-Path $programFilesX86 "Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
        throw (
            "Visual Studio Installer/vswhere.exe não foi encontrado. " +
            "Instale Visual Studio Build Tools 2022 com o componente " +
            "'Desktop development with C++'."
        )
    }
    $arguments = @(
        "-latest",
        "-version", "[17.0,18.0)",
        "-products", "*",
        "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
        "-property", "installationPath"
    )
    $lines = @(Invoke-CheckedNative -FilePath $vswhere -ArgumentList $arguments `
            -Activity "Localização do Visual Studio Build Tools" -CaptureOutput)
    $installationPath = ($lines | Where-Object { $_ } | Select-Object -First 1).ToString().Trim()
    if (-not $installationPath -or -not (Test-Path -LiteralPath $installationPath)) {
        throw (
            "Visual Studio Build Tools com C++ não foi encontrado. " +
            "Abra o Visual Studio Installer e adicione 'Desktop development with C++'."
        )
    }
    $vsDevCmd = Join-Path $installationPath "Common7\Tools\VsDevCmd.bat"
    if (-not (Test-Path -LiteralPath $vsDevCmd -PathType Leaf)) {
        throw "VsDevCmd.bat não foi encontrado na instalação: $installationPath"
    }
    $versionLines = @(
        Invoke-CheckedNative -FilePath $vswhere -ArgumentList @(
            "-latest", "-version", "[17.0,18.0)", "-products", "*",
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property", "catalog_productDisplayVersion"
        ) -Activity "Leitura da versão do Visual Studio" -CaptureOutput
    )
    return [PSCustomObject]@{
        InstallationPath = $installationPath
        Version = (($versionLines | Where-Object { $_ } | Select-Object -First 1).ToString().Trim())
        VsDevCmd = $vsDevCmd
        GeneratorInstance = $installationPath
    }
}

function Import-VisualStudioEnvironment {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$VsDevCmd)

    $commandLine = "call `"$VsDevCmd`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
    $environment = @(
        Invoke-CheckedNative -FilePath $env:ComSpec -ArgumentList @("/d", "/s", "/c", $commandLine) `
            -Activity "Inicialização do ambiente do Visual Studio" -CaptureOutput
    )
    foreach ($line in $environment) {
        if ($line -match "^([^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
    if (-not $env:VSCMD_VER) {
        throw "VsDevCmd.bat terminou sem configurar VSCMD_VER."
    }
    Get-RequiredCommandPath -Name "cl.exe" -Guidance "Repare a instalação do compilador C++." |
        Out-Null
}

function Find-WhisperCli {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$WhisperRoot,
        [string]$ManifestCandidate
    )

    $candidates = @()
    if ($ManifestCandidate) {
        $candidates += $ManifestCandidate
    }
    $buildRoot = Join-Path $WhisperRoot "build"
    $candidates += @(
        (Join-Path $buildRoot "bin\Release\whisper-cli.exe"),
        (Join-Path $buildRoot "bin\whisper-cli.exe")
    )
    $resolved = $candidates |
        Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } |
        Select-Object -First 1
    if (-not $resolved) {
        throw (
            "whisper-cli.exe não foi encontrado em build\bin\Release nem em build\bin. " +
            "Execute novamente scripts\windows\instalar.ps1."
        )
    }
    return (Resolve-Path -LiteralPath $resolved).Path
}

function Save-AtomicUtf8Json {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Data,
        [Parameter(Mandatory)][string]$Path
    )

    $temporary = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    $backup = "$Path.$([Guid]::NewGuid().ToString('N')).bak"
    $json = $Data | ConvertTo-Json -Depth 8
    try {
        [IO.File]::WriteAllText($temporary, $json, [Text.UTF8Encoding]::new($false))
        if (Test-Path -LiteralPath $Path) {
            [IO.File]::Replace($temporary, $Path, $backup, $true)
        } else {
            [IO.File]::Move($temporary, $Path)
        }
    } finally {
        Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
    }
}

Export-ModuleMember -Function @(
    "Find-WhisperCli",
    "Get-RequiredCommandPath",
    "Get-VisualStudioInstallation",
    "Import-VisualStudioEnvironment",
    "Invoke-CheckedNative",
    "Save-AtomicUtf8Json"
)
