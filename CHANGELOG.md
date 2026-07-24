# Changelog

O projeto segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e versionamento semântico.

## [Unreleased]

Nenhuma alteração adicional registrada.

## [0.2.0-beta] - 2026-07-24

### Added

- Detecção de Visual Studio Build Tools e carregamento de `VsDevCmd.bat`.
- Manifesto de instalação com versão e ambiente.
- Teste real Windows com fala artificial.
- Preparação PyInstaller `onedir` e Inno Setup, sem binários publicados.

### Changed

- Instalador Windows idempotente com gerador Visual Studio 2022 x64 explícito.
- Modelos baixados no diretório configurado, com tamanho mínimo e SHA-256.
- Descoberta automática do `whisper-cli.exe`.
- Mensagens e documentação Windows orientadas a iniciantes.

### Fixed

- Falso sucesso após falha de build, download ou transcrição.
- Seleção acidental de NMake sem ambiente C++ carregado.
- Divergência entre a pasta de download e a pasta procurada pelo transcritor.
- Reutilização de modelo parcial ou corrompido.

## [0.1.0] - 2026-07-24

- Núcleo FFmpeg → whisper.cpp, CLI, lote e GUI inicial.
- Saídas TXT, SRT, VTT e JSON.
- Scripts, testes, CI, documentação e curso-base.
