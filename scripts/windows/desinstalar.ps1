[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"),
    [switch]$RemoveModels
)

$ResolvedBase = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA "TropaTranscribeLocal"))
$ResolvedTarget = [IO.Path]::GetFullPath($InstallRoot)
if ($ResolvedTarget -ne $ResolvedBase) {
    throw "Por segurança, este script remove somente o diretório padrão: $ResolvedBase"
}
if (-not (Test-Path -LiteralPath $ResolvedTarget)) {
    Write-Host "Nada para remover."
    exit 0
}
$Models = Join-Path $ResolvedTarget "models"
if ((Test-Path $Models) -and -not $RemoveModels) {
    Write-Host "Modelos preservados em: $Models"
    Get-ChildItem -LiteralPath $ResolvedTarget -Force |
        Where-Object { $_.FullName -ne $Models } |
        Remove-Item -Recurse -Force
} elseif ($PSCmdlet.ShouldProcess($ResolvedTarget, "Remover instalação e modelos")) {
    Remove-Item -LiteralPath $ResolvedTarget -Recurse -Force
}
Write-Host "Transcrições fora do diretório de instalação não foram removidas."
