# Changelog

O projeto segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e versionamento semântico.

## [Unreleased]

## [0.3.1-alpha] - 2026-07-24

### Added

- Manifesto Windows x64 imutável com versões, URLs HTTPS, tamanhos, SHA-256,
  licenças, origem, arquivos instalados e comandos de diagnóstico.
- Provisionador por usuário de FFmpeg shared, whisper.cpp e modelos, sem
  compilação, elevação ou alteração do `PATH`.
- Assistente de primeiro uso com consentimento, espaço livre, progresso,
  cancelamento, reparo e diagnóstico.
- Testes de manifesto adulterado, hash incorreto, redirecionamento não
  permitido, path traversal, symlink, cancelamento e DLL inesperada.
- Inno Setup 7.0.2 preparado para instalador experimental app/bootstrap.

### Changed

- Modelos usam revisão imutável e exigem tamanho e SHA-256 exatos.
- Resolução de FFmpeg e whisper.cpp prioriza runtimes locais validados.
- Inventário, SBOM, avisos de terceiros e documentação de licenças passam a
  registrar os componentes concretos.

### Security

- Extração ZIP por allowlist em staging, com promoção atômica e rollback.
- Diagnósticos nativos usam argumentos fixos, `shell=False`, diretório
  confiável e `PATH` reduzido.
- Publicação de executável, instalador, tag, release e bundle segue bloqueada.

## [0.3.0-alpha] - 2026-07-24

### Added

- GUI com fila removível, progresso individual/total, prévia, cópia e acessibilidade.
- Diagnóstico local copiável com redação de caminhos privados.
- Gerenciador de modelos cancelável, atômico e protegido contra exclusão em uso.
- SBOM CycloneDX, manifesto de componentes e geração de hashes SHA-256.
- Preparação de instalador, checklist Windows limpo e aula prática do WhatsApp.

### Changed

- `small` passa a ser a recomendação visual para uso geral em pt-BR.
- Cancelamento é diferenciado de falha e nunca produz mensagem de sucesso.
- Release passa para `0.3.0-alpha`; binários permanecem bloqueados.

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
