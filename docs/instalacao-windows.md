# Instalação no Windows

## 1. Verificar pré-requisitos

Abra PowerShell e execute:

```powershell
git --version
cmake --version
ffmpeg -version
python --version
```

Não é necessário abrir o Developer PowerShell. O instalador localiza o Visual
Studio Build Tools 2022 com `vswhere.exe`, carrega `VsDevCmd.bat` no próprio
processo e confirma `cl.exe`. Instale a carga
**Desktop development with C++** pelo Visual Studio Installer.

CMake também é procurado em `C:\Program Files\CMake` e dentro do Visual Studio.
Uma instalação existente do FFmpeg via WinGet é localizada mesmo quando o
atalho ainda não entrou no `PATH`.

Fontes oficiais: [Git](https://git-scm.com/download/win),
[CMake](https://cmake.org/download/), [Python](https://www.python.org/downloads/windows/)
e [FFmpeg](https://ffmpeg.org/download.html). O projeto não escolhe nem
redistribui um build de FFmpeg nesta fase; confira licença e origem.

## 2. Instalar

Na raiz do repositório:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\scripts\windows\instalar.ps1 -Model small
```

O escopo `Process` termina ao fechar o terminal. O script cria
`%LOCALAPPDATA%\TropaTranscribeLocal`, clona whisper.cpp `v1.9.1`, compila,
cria venv e baixa o modelo. É idempotente e não altera configuração global.
O gerador é fixado em `Visual Studio 17 2022` x64. Se houver cache anterior do
NMake, apenas a pasta `build` do runtime gerenciado é recriada.

## 3. Verificar e usar

```powershell
.\scripts\windows\verificar.ps1
.\scripts\windows\transcrever.ps1 "C:\Midias\audio autorizado.ogg" -Model small
```

Resultado esperado: FFmpeg, `whisper-cli`, modelo, disco, RAM e teste `--help`.

## Problemas reais encontrados

### CMake escolheu NMake

Isso ocorre quando um PowerShell comum não conhece `cl.exe`/`nmake.exe`. A beta
não depende dessa seleção automática: localiza Build Tools, carrega
`VsDevCmd.bat` e escolhe o gerador Visual Studio x64.

### Modelo foi salvo na pasta errada

Não execute o script de download do whisper.cpp a partir da raiz do projeto.
O instalador chama o downloader próprio com `--directory` explícito e grava em:

```text
%LOCALAPPDATA%\TropaTranscribeLocal\models
```

Arquivos parciais usam nome temporário e só substituem o destino após tamanho e
SHA-256 válidos.

### `whisper-cli.exe` não foi encontrado

O projeto procura automaticamente:

```text
runtime\whisper.cpp\build\bin\Release\whisper-cli.exe
runtime\whisper.cpp\build\bin\whisper-cli.exe
```

Execute `verificar.ps1`. Não copie o executável manualmente.

### Uma etapa falhou, mas apareceu sucesso

A versão 0.2.0-beta verifica todos os códigos nativos. Se qualquer clone,
configuração, build, `pip`, download ou transcrição falhar, o script termina
com código diferente de zero e a mensagem **NÃO foi concluída**.

## Teste real

```powershell
.\tests\integration\windows-real-smoke.ps1 -Model small
```

O teste usa uma voz sintética do Windows, sem dados pessoais. Consulte
[`validacao-windows-real.md`](validacao-windows-real.md).

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

## Desktop alpha

O bundle experimental `onedir` é construído com:

```powershell
.\scripts\windows\build-gui.ps1 -PythonPath ".\.venv\Scripts\python.exe"
```

Ele abre sem Python instalado, mas não incorpora FFmpeg/whisper.cpp. O
instalador Inno Setup não instala dependências globais, permite escolher pasta,
mostra licenças e oferece excluir somente modelos na desinstalação. Antes de
usar qualquer instalador, confira hash e
[`validacao-desktop-windows-limpo.md`](validacao-desktop-windows-limpo.md).
