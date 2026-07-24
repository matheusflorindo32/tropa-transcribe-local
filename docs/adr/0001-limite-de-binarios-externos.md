# ADR 0001 — Limite de binários externos no desktop

- Status: aceito para `v0.3.0-alpha`
- Data: 2026-07-24

## Contexto

O executável precisa abrir sem Python instalado. FFmpeg pode ser LGPL ou GPL
conforme os parâmetros da build, e uma distribuição concreta exige registrar
configuração, fontes e obrigações. O `whisper.cpp` e os modelos também precisam
ter origem, versão, hash e licença confirmados por artefato.

## Decisão

O bundle experimental incorpora somente o aplicativo, o runtime Python, Qt/
PySide6 e o bootloader do PyInstaller. FFmpeg, `whisper-cli` e modelos não são
incorporados nesta fase. A GUI diagnostica a ausência desses componentes e o
gerenciador baixa modelos somente após ação do usuário.

## Consequências

O executável abre sem Python, mas uma máquina limpa ainda não transcreve até que
o runtime externo compatível seja provisionado. Esse é um bloqueador explícito
para beta pública, não um motivo para reduzir validações ou instalar ferramentas
globais silenciosamente.
