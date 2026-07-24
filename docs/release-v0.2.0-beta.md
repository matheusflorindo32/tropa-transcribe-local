# Preparação da release v0.2.0-beta

## Escopo

Release de código-fonte para estabilizar instalação e transcrição em Windows.
Não inclui executáveis, modelos, FFmpeg, whisper.cpp compilado ou instalador.

## Destaques

- instalação idempotente com Visual Studio Build Tools detectado;
- falha rápida e códigos de saída confiáveis;
- modelo no diretório configurado, download atômico e integridade;
- descoberta automática do `whisper-cli.exe`;
- manifesto com versão e ambiente;
- teste real com fala artificial;
- estrutura inicial PyInstaller `onedir` e Inno Setup.

## Critérios antes de criar a tag

- [ ] CI da branch e do pull request aprovada.
- [x] Smoke real repetido com `small` no Windows 11.
- [ ] Checklist de máquina limpa executado ou limitações aceitas explicitamente.
- [ ] Diff sem mídia, transcrições, modelos, binários, logs ou segredos.
- [ ] Notas, licenças e hashes revisados.

Tag planejada: `v0.2.0-beta`.

Esta entrega prepara a release; não cria tag nem publica artefato executável.
