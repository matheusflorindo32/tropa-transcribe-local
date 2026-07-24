# Instalação no Windows

## 1. Verificar pré-requisitos

Abra PowerShell e execute:

```powershell
git --version
cmake --version
ffmpeg -version
python --version
Get-Command cl.exe
```

Esperado: versão de cada ferramenta. Se `cl.exe` faltar, abra o terminal
**Developer PowerShell for VS** ou instale Visual Studio Build Tools com
**Desktop development with C++**.

Fontes oficiais: [Git](https://git-scm.com/download/win),
[CMake](https://cmake.org/download/), [Python](https://www.python.org/downloads/windows/)
e [FFmpeg](https://ffmpeg.org/download.html). O projeto não escolhe nem
redistribui um build de FFmpeg nesta fase; confira licença e origem.

## 2. Instalar

Na raiz do repositório:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\scripts\windows\instalar.ps1 -Model base
```

O escopo `Process` termina ao fechar o terminal. O script cria
`%LOCALAPPDATA%\TropaTranscribeLocal`, clona whisper.cpp `v1.9.1`, compila,
cria venv e baixa o modelo. É idempotente e não altera configuração global.

## 3. Verificar e usar

```powershell
.\scripts\windows\verificar.ps1
.\scripts\windows\transcrever.ps1 "C:\Mídia\audio autorizado.ogg"
```

Resultado esperado: FFmpeg, `whisper-cli`, modelo, disco, RAM e teste `--help`.

## Atualizar e remover

Atualizações de whisper.cpp não são automáticas; valide release, flags e testes
antes de alterar `v1.9.1`. Para remover runtime preservando modelos:

```powershell
.\scripts\windows\desinstalar.ps1
```

Para remover também modelos, confirme explicitamente:

```powershell
.\scripts\windows\desinstalar.ps1 -RemoveModels
```

Transcrições fora da pasta da aplicação são preservadas.
