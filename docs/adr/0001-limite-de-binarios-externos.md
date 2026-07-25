# ADR 0001 — Limite de binários externos no desktop

- Status: atualizado para `v0.3.1-alpha`
- Data: 2026-07-24

## Contexto

O executável precisa abrir sem Python instalado. FFmpeg pode ser LGPL ou GPL
conforme os parâmetros da build, e uma distribuição concreta exige registrar
configuração, fontes e obrigações. O `whisper.cpp` e os modelos também precisam
ter origem, versão, hash e licença confirmados por artefato.

## Decisão

O bundle experimental incorpora somente o aplicativo, o runtime Python, Qt/
PySide6 e o bootloader do PyInstaller. FFmpeg, `whisper-cli` e modelos não são
incorporados nesta fase. O assistente baixa componentes somente após ação do
usuário, usando manifesto fixo, tamanhos/hashes exatos, staging e diagnóstico.

## Consequências

O executável abre sem Python e o usuário consegue preparar a máquina sem
toolchain. O primeiro uso ainda precisa de rede e espaço para os downloads. A
publicação segue bloqueada até a validação completa em Windows 11 limpo,
assinatura, Defender/SmartScreen e revisão das licenças concretas.
