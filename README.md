# Tropa Transcribe Local

> [INSERIR LOGO]

Transcrição local e privada de áudio e vídeo, com foco inicial em português
brasileiro. O projeto integra FFmpeg e whisper.cpp, oferece CLI, interface
gráfica opcional e materiais do curso livre da Tropa Científica.

> **Aviso de precisão:** A transcrição é gerada automaticamente e pode conter
> erros. Revise nomes, números, termos técnicos e informações críticas antes de
> utilizar ou publicar o conteúdo.

Tropa Transcribe Local é um projeto independente da Tropa Científica. Utiliza
e integra tecnologias open source de terceiros, respeitando seus respectivos
autores e termos de licença. Não existe afiliação oficial com a OpenAI,
ggml-org ou FFmpeg.

## Objetivos e recursos

- processamento local por padrão, sem conta, API, telemetria ou upload;
- arquivos OGG, OPUS, MP3, WAV, M4A, AAC, FLAC, MP4, MOV, MKV e WEBM,
  convertidos pelo FFmpeg para WAV PCM mono 16 kHz;
- exportação TXT, SRT, VTT e JSON pelo `whisper-cli`;
- seleção de idioma e modelos multilíngues;
- lote, caminhos com espaços e Unicode, modo silencioso e cancelamento;
- GUI opcional em PySide6, com arrastar e soltar e worker thread;
- Windows como prioridade do MVP; Linux e macOS em estágio experimental.

O suporte depende dos codecs habilitados na instalação local do FFmpeg. Os
formatos listados são aceitos pelo validador, mas cada variante de codec deve
ser confirmada no computador de destino.

## Demonstração

```text
[INSERIR GIF OU CAPTURAS DE TELA APÓS VALIDAÇÃO VISUAL]
```

## Requisitos

- Windows 10/11 (prioritário), Linux ou macOS;
- Python 3.11 ou 3.12;
- Git, CMake e compilador C++ para compilar whisper.cpp;
- FFmpeg disponível no `PATH`;
- espaço para modelo, áudio temporário e saídas.

O instalador fixa o whisper.cpp em `v1.9.1`. Consulte
[`docs/fontes-tecnicas.md`](docs/fontes-tecnicas.md).

## Instalação rápida no Windows

Abra o PowerShell na raiz do repositório:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\scripts\windows\instalar.ps1 -Model base
.\scripts\windows\verificar.ps1
```

O script não instala ferramentas globais, não solicita credenciais e não
desativa proteções. Se faltar uma dependência, ele para e apresenta orientação.
Guia completo: [`docs/instalacao-windows.md`](docs/instalacao-windows.md).

Para desenvolvimento:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,gui]"
```

## Uso

```powershell
tropa-transcribe "audio.ogg"
tropa-transcribe "video.mp4" --model small
tropa-transcribe "entrevista.wav" --language pt
tropa-transcribe "pasta" --batch
tropa-transcribe "audio.m4a" --output txt srt vtt
tropa-transcribe "audio.ogg" --output-dir "transcricoes"
tropa-transcribe "audio.wav" --keep-temp
tropa-transcribe "audio.mp3" --verbose
tropa-transcribe --help
```

Para apontar componentes fora do `PATH`:

```powershell
tropa-transcribe audio.wav `
  --ffmpeg "C:\Ferramentas\ffmpeg.exe" `
  --whisper-cli "C:\whisper.cpp\build\bin\Release\whisper-cli.exe" `
  --model-path "C:\Modelos\ggml-base.bin"
```

Interface:

```powershell
python -m pip install -e ".[gui]"
tropa-transcribe-gui
```

## Modelos

| Modelo | Disco aproximado | Memória aproximada | Perfil |
|---|---:|---:|---|
| tiny | 75 MiB | 273 MB | testes e máquinas limitadas |
| base | 142 MiB | 388 MB | início recomendado |
| small | 466 MiB | 852 MB | melhor qualidade geral |
| medium | 1,5 GiB | 2,1 GB | maior qualidade, mais lento |
| large | 2,9 GiB | 3,9 GB | hardware robusto |

Valores são referências do whisper.cpp e variam conforme versão, quantização e
hardware. Modelos não são versionados no Git. Baixe com:

```powershell
python tools\download_model.py base
```

O downloader restringe nomes e origem, grava de modo atômico, calcula SHA-256
e valida o ETag SHA-256 quando o servidor LFS o fornece.

## Privacidade, segurança e limitações

Nenhum conteúdo é enviado pelo código do projeto. WAV temporário é criado na
pasta de dados local do aplicativo e removido ao final, salvo com
`--keep-temp`. Saídas vão para a pasta escolhida. O sistema não garante, por si
só, conformidade com a LGPD: base legal, autorização, finalidade, retenção,
acesso e descarte continuam sob responsabilidade do usuário ou controlador.

A ferramenta não substitui transcrição certificada, laudo, perícia, prontuário
revisado, ata oficial, parecer jurídico, revisão profissional ou legenda
humana em contexto crítico.

Leia [`PRIVACY.md`](PRIVACY.md), [`SECURITY.md`](SECURITY.md),
[`DISCLAIMER.md`](DISCLAIMER.md) e [`docs/limitacoes.md`](docs/limitacoes.md).

## Solução de problemas

Execute:

```powershell
python tools\check_environment.py
.\scripts\windows\verificar.ps1
```

Consulte [`docs/solucao-de-problemas.md`](docs/solucao-de-problemas.md).

## Curso Tropa Científica

O diretório [`course/`](course/) contém a base de 20 horas do curso
**Transcrição Local com Inteligência Artificial — Whisper, privacidade,
automação e aplicações profissionais**.

[INSERIR LINK DO CURSO]

## Roadmap, contribuição e segurança

- [`ROADMAP.md`](ROADMAP.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`SECURITY.md`](SECURITY.md)
- [`SUPPORT.md`](SUPPORT.md)

Relate vulnerabilidades de forma privada para:
`[INSERIR E-MAIL INSTITUCIONAL]`.

## Licença e créditos

O código autoral deste repositório usa a licença MIT. Dependências mantêm suas
próprias licenças; FFmpeg pode ser LGPL ou GPL conforme a compilação, PySide6
é LGPLv3/GPLv3 ou comercial, e Whisper/whisper.cpp são MIT. Não distribuímos
binários de terceiros nesta fase. Leia [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

Contato institucional: `[INSERIR E-MAIL INSTITUCIONAL]`.
